"""Module des modeles de donnees du jeu
Ce module contient les classes qui representent les objets du jeu ainsi
que le modèle de base du jeu.
"""
from __future__ import annotations

from ast import literal_eval
from random import randrange, choice

from Orion_client.model.building import *
from Orion_client.helper import get_prochain_id, AlwaysInt, CommandQueue, \
    StringTypes
from Orion_client.model import ships
from Orion_client.model.building import Building
from Orion_client.model.ressource import Ressource
from Orion_client.model.ships import Ship, Flotte
from Orion_client.model.space_object import TrouDeVers, Etoile
import math


class Modele:
    """Classe du modèle.
    Le modèle contient les données du jeu.
    :ivar largeur: La largeur du jeu
    :ivar hauteur: La hauteur du jeu
    :ivar trou_de_vers: La liste des trous de ver.
    :ivar etoiles: La liste des étoiles
    :ivar joueurs: le dictionnaire des joueurs
    : La queue de communication entre le modèle et
     le modèle local
    :ivar log: Le dictionnaire des logs
    :param joueurs: Les joueurs du jeu
    """

    def __init__(self, joueurs, username: str):
        """Initialise le modèle.
        :param joueurs: Les joueurs du jeu
        """
        self.controller_username = username
        self.cadre: int = 0

        self.largeur: int = 9000
        self.hauteur: int = 9000

        self.trou_de_vers: list = []
        self.etoiles: list = []
        self.joueurs: dict = {}

        self.local_queue: CommandQueue = CommandQueue()
        self.log: dict = {}

        with open("assets/planet.csv", "r") as planet_name_csv:

            planet_name_csv = planet_name_csv.read().split("\n")

        self.creer_trou_de_vers(int((self.hauteur * self.largeur) / 5000000))
        self.creer_etoiles(int((self.hauteur * self.largeur) / 500000),
                           planet_name_csv)
        self.creer_joueurs(joueurs, planet_name_csv)
        self.creer_ias(planet_name_csv)

    def change_planet_ownership(self, planet_id: str,
                                new_owner: None | str = None,
                                old_owner: None | str = None):
        """Change la propriété des planètes en fonction de la distance
        entre les vaisseaux et les planètes.
        """
        planet = self.get_object(planet_id, StringTypes.ETOILE)
        # Todo : Optimize Etoile and Etoile occupe from received tag list.
        if planet:
            if new_owner is None:
                self.joueurs[old_owner].etoiles_controlees.remove(planet)
                self.etoiles.append(planet)
                planet.proprietaire = None
                planet.couleur = "grey"
            else:
                self.etoiles.remove(planet)
                self.joueurs[new_owner].conquer_planet(planet)

    def target_change_request(self, ship_informations: dict, target: dict):
        """Demande de changement de cible d'un vaisseau.
        """
        player_ship = self.get_object(ship_informations["id"],
                                      ship_informations["type"])

        new_pos = target["pos"]
        if "id" in target:
            new_target = self.get_object(target["id"], target["type"])
            player_ship.target_change(new_pos, new_target)
        else:
            player_ship.target_change(new_pos)

    def get_object(self, object_id, object_type=None,
                   owner=None) -> None | Ship | Flotte | TrouDeVers | Etoile:
        """Retourne un objet du jeu.
        :param object_id: L'id de l'objet
        :param object_type: Le type de l'objet
        :param owner: Le propriétaire de l'objet
        :return: L'objet demandé
        """
        temp_object = None
        if object_type:
            if object_type in StringTypes.ship_types():
                temp_object = self.__get_ship(object_id, owner=owner)

            elif object_type in StringTypes.planet_types():
                temp_object = self.__get_etoile(object_id)

        else:
            temp_object = self.__get_ship(object_id, owner=owner)
            if not temp_object:
                temp_object = self.__get_etoile(object_id)

        if not temp_object:
            print(f"Object not found in get_object with parameter : "
                  f"{object_id}, {object_type}, {owner}")

        return temp_object

    def __get_etoile(self, etoile_id):
        """Retourne une étoile.
        """
        for etoile in self.etoiles:
            if etoile.id == etoile_id:
                return etoile

        for joueur in self.joueurs.values():
            etoile = joueur.get_etoile_by_id(etoile_id)
            if etoile:
                return etoile

    def __get_ship(self, ship_id, ship_type=None, owner=None):
        """Retourne un vaisseau.
        :param ship_id: L'id du vaisseau
        :param ship_type: Le type du vaisseau
        :param owner: Le propriétaire du vaisseau
        """
        if owner:
            return self.joueurs[owner].get_ship(ship_id, ship_type)
        else:
            for joueur in self.joueurs.values():
                ship = joueur.get_ship(ship_id, ship_type)
                if ship:
                    return ship

    def receive_action(self, funct: str, args: list):
        """Reçoit une action du serveur et l'ajoute dans la queue.
        :param funct: La fonction à appeler
        :param args: les arguments de la fonction
        """
        getattr(self, funct)(*args)

    def tick(self, cadre: int):
        """Joue le prochain coup pour chaque objet.
        Ne pas modifier.
        :param cadre: le cadre a joué (frame)
        """
        for i in self.log:
            for m in self.log[i]:
                if self.log[i].count(m) > 1:
                    self.log[i].remove(m)
            for j in self.log:
                if i != j:
                    for k in self.log[i]:
                        if k in self.log[j]:
                            self.log[j].remove(k)

        self.cadre = cadre
        if cadre in self.log:
            for i in self.log[cadre]:
                if i:
                    username = i[0]
                    action = i[1][0]
                    args = i[1][1:]
                    if username == "model":
                        self.receive_action(action, args)
                    else:
                        self.joueurs[username].receive_action(action, args)

            del self.log[cadre]

        for i in self.joueurs:
            self.joueurs[i].tick()

        for i in self.trou_de_vers:
            i.tick()

        self.local_queue.execute(self)

    def ajouter_actions(self, actionsrecues: list, frame: int):
        """Ajoute les actions reçues dans la liste des actions à faire
         si et seulement si le cadre est plus petit que le cadre courant.
        :param actionsrecues: La liste des actions reçues du serveur
        :param frame: le cadre courant
        """
        for i in actionsrecues:
            cadrecle = i[0]
            if cadrecle:
                if (frame - 1) > int(cadrecle):
                    raise Exception("Le cadre est plus petit que le cadre ")
                action = literal_eval(i[1])
                if cadrecle not in self.log.keys():
                    self.log[cadrecle] = action
                else:
                    self.log[cadrecle] = self.log[cadrecle] + action

    def creer_trou_de_vers(self, num_wormholes: int):
        """Crée n trous de vers.
        :param num_wormholes: le nombre de trous de vers à créer"""
        for _ in range(num_wormholes):
            x1 = randrange(10, self.largeur - 10)
            y1 = randrange(10, self.hauteur - 10)
            x2 = randrange(10, self.largeur - 10)
            y2 = randrange(10, self.hauteur - 10)
            self.trou_de_vers.append(TrouDeVers(x1, y1, x2, y2))

    def creer_etoiles(self, nb_etoiles: int, planet_name_csv):
        """Crée des étoiles, d'une certaine couleur dépendant du joueur.
        :param nb_etoiles: le nombre d'étoiles à créer
        """
        bordure = 10
        self.etoiles = [
            Etoile(randrange(self.largeur - (2 * bordure)) + bordure,
                   randrange(self.hauteur - (2 * bordure)) + bordure,
                   self.local_queue, planet_name_csv)
            for _ in range(nb_etoiles)]

    def creer_joueurs(self, joueurs: list, planet_name_csv):
        """Créé les joueurs et leur attribue une etoile mère.
        :param joueurs: la liste des joueurs à créer
        """
        couleurs = ["red", "blue", "lightgreen", "yellow", "lightblue", "pink",
                    "gold", "purple"]
        etoiles_occupee = []
        for i in range(len(joueurs)):
            p = choice(self.etoiles)
            etoiles_occupee.append(p)
            self.etoiles.remove(p)

        for i, joueur in enumerate(joueurs):
            etoile = etoiles_occupee[i]
            self.joueurs[joueur] = Joueur(joueur, etoile, couleurs.pop(0),
                                          self.local_queue,
                                          self.controller_username)
            for e in range(5):
                self.etoiles.append(
                    Etoile(randrange(etoile.x - 500, etoile.x + 500),
                           randrange(etoile.y - 500, etoile.y + 500),
                           self.local_queue, planet_name_csv)
                )

    def creer_ias(self, planet_name_csv, ias: int = 0):
        """Créer les IAs et leur attribue une etoile mère.
        :param ias: le nombre d'IA à créer
        """
        couleurs_ia = ["orange", "green", "cyan", "SeaGreen1", "turquoise1",
                       "firebrick1"]
        etoiles_occupee = []
        for i in range(ias):
            p = choice(self.etoiles)
            etoiles_occupee.append(p)
            self.etoiles.remove(p)
        for i in range(ias):
            self.joueurs[f"IA_{i}"] = AI(f"IA_{i}", etoiles_occupee.pop(0),
                                         couleurs_ia.pop(0),
                                         self.local_queue,
                                         self.controller_username)

    def is_owner_and_is_type(self, tags_list: list[str],
                             object_type: str | list[str]) -> bool:
        """Retourne True si l'objet est de type object_type
        et que l'utilisateur"""
        return self.is_type(tags_list, object_type) \
            and self.is_owner(tags_list)

    @staticmethod
    def is_type(tags_list: list, object_type: str | list[str]) -> bool:
        """Retourne True si l'objet est de type object_type"""
        if isinstance(object_type, list):
            return any(tag in object_type for tag in tags_list)
        return object_type in tags_list

    def is_owner(self, tags_list) -> bool:
        """Retourne True si l'objet appartient au joueur de cette vue."""
        return self.controller_username in tags_list


class Joueur:
    """Classe du joueur.
    Le joueur est le personnage qui joue le jeu.
    Il possede une flotte de vaisseaux, une liste d'etoiles controlees et une
    liste d'actions.
    :ivar id: l'id du joueur
    :ivar nom: le nom du joueur
    :ivar couleur: la couleur du joueur
    :ivar flotte: la flotte du joueur
    :ivar etoile_mere: l'etoile mere du joueur
    :ivar etoiles_controlees: la liste des etoiles controlees par le joueur
    :ivar consommation_energie_joueur: la consommation d'energie du joueur
    :param nom: le nom du joueur
    :param etoile_mere: l'etoile mere du joueur
    :param couleur: la couleur du joueur
    """

    def __init__(self, nom: str, etoile_mere: Etoile, couleur: str,
                 local_queue: CommandQueue,
                 controller_owner: str):
        """Initialise le joueur.
        :param nom: le nom du joueur
        :param etoile_mere: l'etoile mere du joueur
        :param couleur: la couleur du joueur
        """
        self.id: str = get_prochain_id()
        """L'id du joueur."""
        self.nom = nom
        self.etoile_mere = etoile_mere
        self.etoile_mere.transit = True
        self.etoile_mere.buildinglist = [Farm(), Mine()]
        self.etoile_mere.proprietaire = self.nom
        """Le nom du joueur."""
        self.is_controller_owner = controller_owner == nom
        self.couleur = couleur
        """La couleur du joueur."""
        self.flotte: Flotte = Flotte()
        """Flotte du joueur."""
        self.etoiles_controlees: list = [etoile_mere]
        """Liste des etoiles controlees par le joueur."""
        self.consommation_energie_joueur = AlwaysInt(10)
        """Ressources totales du joueur."""

        self.local_queue = local_queue
        """Queue de commandes du modèle au controller."""

        self.ressources = Ressource(metal=100, beton=100, energie=100,
                                    nourriture=100, population=0,
                                    science=0)
        """L'etoile mere du joueur."""
        self.etoile_mere.couleur = couleur
        self.etoile_mere.proprietaire = self.nom

        self.recently_lost_ships_id = []

    def conquer_planet(self, etoile: Etoile):
        """Conquiert une etoile et lui établie les charactérisques
        du joueur.
        :param etoile: l'etoile à conquérir
        """
        etoile.proprietaire = self.nom
        etoile.couleur = self.couleur
        etoile.resistance = 50
        etoile.need_refresh = False
        self.etoiles_controlees.append(etoile)

    def action_from_server(self, funct: str, args: list):
        """Fonction qui active une action du joueur reçue du serveur en
        fonction de la fonction et des arguments envoyés.
        :param funct: la fonction à activer
        :param args: les arguments de la fonction
        """
        getattr(self, funct)(*args)

    def construct_ship(self, planet_id, type_ship):
        """
        Déclenche la construction d'un vaisseau sur une planète dépendant
        du type de vaisseau demandé.
        :param planet_id: l'id de la planète sur laquelle construire
        le vaisseau
        :param type_ship: le type de vaisseau à construire
        """
        pos = self.get_etoile_by_id(planet_id).position
        ship = getattr(ships, type_ship.capitalize())(
            pos, self.nom, self.local_queue
        )

        if ship:
            self.flotte[type_ship][ship.id] = ship

    def remove_ship(self, ship_id: str, ship_type: str):
        """Supprime un vaisseau de la flotte du joueur.
        :param ship_id: l'id du vaisseau à supprimer
        :param ship_type: le type du vaisseau à supprimer
        """
        if ship_id in self.flotte[ship_type]:
            self.recently_lost_ships_id.append(ship_id)
            del self.flotte[ship_type][ship_id]

    def construct_ship_request(self, planet_id: str, type_ship: str):
        """Fonction que est reçu du serveur depuis la vue du jeu.
        Elle s'assure que la construction d'un vaisseau est possible et
        la déclenche si elle l'est."""
        has_enough_ressources: bool = True  # Pour debug
        # todo : Ressource check
        if type_ship == "militaire":
            pass
        elif type_ship == "transport":
            pass
        elif type_ship == "reconnaissance":
            pass

        if has_enough_ressources:
            self.construct_ship(planet_id, type_ship)

    def deplete_energy(self):
        """
        Consommation des ressources de la flotte de vaisseaux et
        des structures du joueur.
        Compile la quantité d'énergie consommée que requiert les différents
        bâtiments et vaisseaux à la disposition du joueur puis réaffecte la
        quantité d'énergie disponible au joueur.
        """
        conso_structures: int = 0
        conso_vaisseaux: int = 0
        # Consommation d'énergie des structures du joueur
        for e in self.etoiles_controlees:
            for b in e.buildinglist:
                if isinstance(b, Building):
                    conso_structures += b.consumption

        # Consommation des vaisseaux de la flotte du joueur.
        for key, value in self.flotte.items():
            if isinstance(value, Ship):
                value = [value]
        # for vaisseau in value:
        #  if not vaisseau.docked:
        #        conso_vaisseaux += vaisseau.consommation
        # Todo: Ajouter les variables bool docked et int consommation
        #  dans le modele vaisseau (2e sprint)

        self.ressources["energie"] -= AlwaysInt(
            (
                    conso_vaisseaux + conso_structures +
                    self.consommation_energie_joueur))

    def get_etoile_by_id(self, etoile_id: str) -> Etoile | None:
        """Renvoie l'étoile correspondant à l'id donné.
        :param etoile_id: Id de l'étoile
        :return: l'étoile correspondant à l'id
        """
        for i in self.etoiles_controlees:
            if i.id == etoile_id:
                return i
        return None

    def get_ship(self, ship_id: str,
                 ship_type: str | None = None) -> Ship | None:
        """Renvoie le vaisseau correspondant à l'id donné.
        :param ship_id: L'id du vaisseau
        :param ship_type: Le type du vaisseau
        :return: le vaisseau correspondant à l'id
        """
        if ship_type == StringTypes.VAISSEAU:
            ship_type = None

        if ship_type:
            for i in self.flotte[ship_type].values():
                if i.id == ship_id:
                    return i
        else:
            for key in self.flotte.keys():
                for i in self.flotte[key].values():
                    if i.id == ship_id:
                        return i

    def receive_action(self, funct: str, args: list):
        """Fonction qui active une action du joueur reçue du serveur en
        fonction de la fonction et des arguments envoyés.
        :param funct: la fonction à activer
        :param args: les arguments de la fonction
        """
        getattr(self, funct)(*args)

    def tick(self):
        """Fonction de jeu du joueur pour un tour.
        """
        for type_ship in self.flotte.keys():
            for ship in self.flotte[type_ship]:
                self.flotte[type_ship][ship].tick()

        self.ressources_cumul()
        self.increment_pop()

    def ressources_cumul(self):
        for e in self.etoiles_controlees:
            if e.transit:
                planet_res: Ressource = {}
                for key in e.output:
                    planet_res[key] = e.output[key]

                for b in e.buildinglist:
                    if isinstance(b, PowerPlant):
                        planet_res += b.output
                    elif isinstance(b, ResearchCenter):
                        continue
                    else:
                        for key in planet_res:
                            planet_res[key] = planet_res[key] * b.output[key]

                self.ressources += planet_res

    def increment_pop(self):
        tot_population: float = 0
        nourriture_total = 0
        pop_cx: float

        for p in self.etoiles_controlees:
            tot_population += p.population
        #nourriture_total = self.ressources["nourriture"]

        #self.ressources["nourriture"] -= tot_population
        """Consommation de nourriture par tour"""
        print(self.nom , "population du joueur avant calcul: ",tot_population)

        self.ressources["nourriture"] -= (tot_population / 1000)
        print(self.nom , "population du joueur après calcul: ",tot_population)

        """Coéfficient de croissance ou décroissance"""
        pop_cx = self.ressources["nourriture"] / tot_population
        #/ len(self.etoiles_controlees)

        #if pop_cx > 1:
        for c in self.etoiles_controlees:
            c.population = math.ceil(c.population * pop_cx)
        print(self.nom, pop_cx)
        #print(self.nom, self.ressources["nourriture"])





class AI(Joueur):
    """Classe de l'AI.
    L'AI est le personnage non-joueur qui joue le jeu.
    :ivar id: l'id du joueur
    :ivar nom: le nom du joueur
    :ivar couleur: la couleur du joueur
    :ivar flotte: la flotte du joueur
    :ivar etoile_mere: l'etoile mere du joueur
    :ivar etoiles_controlees: la liste des etoiles controlees par le joueur
    :ivar consommation_energie_joueur: la consommation d'enrgie du joueur
    :param nom: le nom du joueur
    :param etoile_mere: l'etoile mere du joueur
    :param couleur: la couleur du joueur
    """

    def __init__(self, nom: str,
                 etoile_mere: Etoile, couleur: str,
                 local_queue, owner) -> None:
        """Initialise l'AI.
        :param nom: le nom de l'AI
        :param etoile_mere: l'etoile mere de l'AI
        :param couleur: la couleur de l'AI
        """
        Joueur.__init__(self, nom, etoile_mere, couleur,
                        local_queue, owner)
        self.cooldownmax: int = 1000
        """Cooldown max de l'AI avant son prochain vaisseau."""
        self.cooldown: int = 20
        """Cooldown en cours de l'AI avant son prochain vaisseau."""
