"""Module des modeles de donnees du jeu

Ce module contient les classes qui representent les objets du jeu ainsi
que le modèle de base du jeu.
"""
from __future__ import annotations
# Ajouté afin de permettre le type hinting sur les classes
# qui se référencent mutuellement
from typing import Callable

# -*- coding: utf-8 -*-
##  version 2022 14 mars - jmd

from random import randrange, choice
from ast import literal_eval

from Orion_client.helper import get_prochain_id, AlwaysInt
from Orion_client.model import ships
from Orion_client.model.building import Building
from Orion_client.model.ships import Ship, Transportation, Militaire, \
    Reconnaissance, Flotte
from Orion_client.model.space_object import TrouDeVers, Etoile
from Orion_client.model.ressource import Ressource


class Modele:
    """Classe du modèle.

    Le modèle contient les données du jeu.
    """

    def __init__(self, joueurs, command_queue):
        """Initialise le modèle.

        :param joueurs: les joueurs du jeu
        """
        self.command_queue = command_queue
        self.largeur: int = 9000
        self.hauteur: int = 9000

        self.joueurs: dict = {}
        self.log: dict = {}

        self.etoiles: list = []
        self.trou_de_vers: list = []

        self.creer_etoiles(int((self.hauteur * self.largeur) / 500000))
        self.creer_joueurs(joueurs)
        self.creer_ias(1)

        self.creer_trou_de_vers(int((self.hauteur * self.largeur) / 5000000))

    def update_ship_target(self, ship_id, owner: str, updatee_id: str,
                           updatee_owner: str):
        # todo : Maybe add kwargs in target change ?
        ship = self.get_ship(ship_id, owner)
        ship_to_update = self.get_ship(updatee_id, updatee_owner)

        if ship and ship_to_update:
            ship_to_update.target_change(ship_to_update.position)

    def update_etoiles_ownership(self, planet_id, new_owner: str):
        etoile = self.get_etoile(planet_id)
        if etoile:
            etoile.proprietaire = new_owner
            self.etoiles.remove(etoile)
            self.joueurs[new_owner].etoiles_controlees.append(etoile)

    def get_etoile(self, planet_id, owner:str | None = None):
        if owner is None:
            for i in self.etoiles:
                if i.id == planet_id:
                    return i

    def get_ship(self, ship_id, owner):
        for ship in self.joueurs[owner].flotte:
            if ship.id == ship_id:
                return ship

    def attack_request(self, owner, ship_id , target_id, target_owner):
        print("attack request")
        print(owner, ship_id, target_id, target_owner)

    def receive_server_action(self, funct: str, args: list):
        """Reçoit une action du serveur et l'ajoute dans la queue.

        :param funct: la fonction à appeler
        :param args: les arguments de la fonction
        """
        getattr(self, funct)(*args)

    def tick(self, cadre):
        """Joue le prochain coup pour chaque objet.

        :param cadre: le cadre à jouer (frame)
        """

        #  NE PAS TOUCHER LES LIGNES SUIVANTES  #################
        # insertion de la prochaine action demandée par le joueur
        if cadre in self.log:
            for i in self.log[cadre]:
                # print("action recue", i)
                # Ici, if i[0] == model j'envoie l'action au model
                # Sinon, je l'envoie au joueur
                if i:
                    print("action recue", i)
                    if i[0] == "model":
                        self.receive_server_action(i[1], i[2])
                    else:
                        self.joueurs[i[0]].receive_server_action(i[1], i[2])
                """
                i a la forme suivante [nomjoueur, action, [arguments]
                alors self.joueurs[i[0]] -> trouve l'objet représentant le joueur de ce nom
                """
            del self.log[cadre]
        # FIN DE L'INTERDICTION #################################

        temp = []
        for i in self.joueurs:
            self.joueurs[i].tick()

        for i in self.trou_de_vers:
            i.tick()

    def ajouter_actions(self, actionsrecues: list, frame: int):
        """Ajoute les actions reçue dans la liste des actions à faire
         si et seulement si le cadre est plus petit que le cadre courant.

        :param actionsrecues: la liste des actions reçues du serveur
        :param frame: le cadre courant
        """
        for i in actionsrecues:
            cadrecle = i[0]
            if cadrecle:
                if (frame - 1) > int(cadrecle):
                    print("PEUX PASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
                action = literal_eval(i[1])

                if cadrecle not in self.log.keys():
                    self.log[cadrecle] = action
                else:
                    self.log[cadrecle].append(action)

    def get_all_players_static_ships_positions(self):
        """Renvoie la position de tous les vaisseaux des joueurs qui ne bougent
        pas.

        :return: la position de tous les vaisseaux des joueurs
        """
        positions = []
        for i in self.joueurs:
            positions += self.joueurs[i].get_all_static_ships_positions()
        return positions

    def get_all_planets_positions(self):
        """Renvoie la position de toutes les planètes.

        :return: la position de tous les planètes
        """
        positions = []
        for i in self.etoiles:
            positions.append(i.position)
        return positions

    def get_id_by_username(self, nom: str) -> str | None:
        """Renvoie l'id du joueur correspondant au nom d'utilisateur.

        :param nom: le nom d'utilisateur
        :return: l'id du joueur
        """
        for joueur in self.joueurs.values():
            if joueur.nom == nom:
                return joueur.id
        return None

    def creer_trou_de_vers(self, num_wormholes: int):
        """Crée n trous de vers.

        :param num_wormholes: le nombre de trous de vers à créer"""
        for _ in range(num_wormholes):
            x1 = randrange(10, self.largeur - 10)
            y1 = randrange(10, self.hauteur - 10)
            x2 = randrange(10, self.largeur - 10)
            y2 = randrange(10, self.hauteur - 10)
            self.trou_de_vers.append(TrouDeVers(x1, y1, x2, y2))

    def creer_etoiles(self, nb_etoiles: int):
        """Crée des étoiles, d'une certaine couleur dépendant du joueur.

        :param nb_etoiles: le nombre d'étoiles à créer
        """
        bordure = 10
        self.etoiles = [
            Etoile(self, randrange(self.largeur - (2 * bordure)) + bordure,
                   randrange(self.hauteur - (2 * bordure)) + bordure)
            for _ in range(nb_etoiles)]

    def creer_joueurs(self, joueurs: list):
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
                                          self.command_queue)
            for e in range(5):
                self.etoiles.append(
                    Etoile(self, randrange(etoile.x - 500, etoile.x + 500),
                           randrange(etoile.y - 500, etoile.y + 500)))

    def creer_ias(self, ias: int = 0):
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
                                         self.command_queue)


class Joueur:
    """Classe du joueur.

    Le joueur est le personnage qui joue le jeu.
    Il possede une flotte de vaisseaux, une liste d'etoiles controlees et une
    liste d'actions.
    """

    def __init__(self, nom: str, etoile_mere: Etoile, couleur: str,
                 command_queue):
        """Initialise le joueur.

        :param parent: le jeu auquel le joueur appartient
        :param nom: le nom du joueur
        :param etoile_mere: l'etoile mere du joueur
        :param couleur: la couleur du joueur
        """
        self.command_queue = command_queue

        self.consommation_joueur = AlwaysInt(10)
        self.energie = AlwaysInt(10000)
        self.id: str = get_prochain_id()
        self.nom = nom

        self.etoile_mere = etoile_mere
        self.etoile_mere.couleur = couleur
        self.etoile_mere.proprietaire = self.nom

        self.couleur = couleur
        self.log: list = []
        """Liste des actions du joueur."""
        self.etoiles_controlees: list = [etoile_mere]
        """Liste des etoiles controlees par le joueur."""

        self.flotte: Flotte = Flotte()
        """Flotte du joueur."""

        self.ressources_total = Ressource(metal=100, beton=100, energie=500,
                                          nourriture=100)

    def tick(self):
        """Fonction de jeu du joueur pour un tour.
        """
        logs = []
        for type_ship in self.flotte.keys():
            for ship in self.flotte[type_ship]:
                self.flotte[type_ship][ship].tick()
                if self.flotte[type_ship][ship].log:
                    for i in self.flotte[type_ship][ship].log:
                        logs.append(i)
                    self.flotte[type_ship][ship].log = []

        for log in logs:
            self.command_queue.add("model", log[0], self.nom, log[1], log[2], log[3])

    def receive_server_action(self, funct: str, args: list):
        """Fonction qui active une action du joueur reçue du serveur en
        fonction de la fonction et des arguments envoyés.

        :param funct: la fonction à activer
        :param args: les arguments de la fonction

        """
        getattr(self, funct)(*args)

    def construct_ship_request(self, planet_id: str, type_ship: str):
        """Fonction que est reçu du serveur depuis la vue du jeu. Elle s'assure que la construction
        d'un vaisseau est possible et la déclenche si elle l'est."""
        has_enough_ressources: bool = True  # Pour debug
        if type_ship == "militaire":
            pass
        elif type_ship == "transport":
            pass
        elif type_ship == "reconnaissance":
            pass

        if has_enough_ressources:
            self.construct_ship(planet_id, type_ship)

    def construct_ship(self, planet_id, type_ship):
        """Déclenche la construction d'un vaisseau sur une planète dépendant
        du type de vaisseau demandé.

        :param planet_id: l'id de la planète sur laquelle construire le vaisseau
        :param type_ship: le type de vaisseau à construire
        """
        pos = self.get_etoile_by_id(planet_id).position
        ship = getattr(ships, type_ship.capitalize())(pos, self.nom)

        if ship:
            self.flotte[type_ship][ship.id] = ship

    def ship_target_change_request(self, ship_id: str, ship_type, pos: tuple):
        """Fonction qui est envoyé depuis la serveyr, via la vue, afin de
        changer la cible du vaisseau si possible.

        :param ship_id: l'id du vaisseau à déplacer
        :param ship_type: le type du vaisseau à déplacer
        :param pos: la position cible du vaisseau
        """
        self.flotte[ship_type][ship_id].target_change(pos)

    def ship_target_to_attack_request(self, ship_id: str, ship_type: str,
                                      target_id: str, target_type: str,
                                      position: tuple):
        """Fonction qui est envoyé depuis la serveyr, via la vue, afin de
        changer la cible du vaisseau si possible.

        :param ship_id: l'id du vaisseau à déplacer
        :param ship_type: le type du vaisseau à déplacer
        :param target_id: l'id de la cible du vaisseau
        """
        print("ship_target_to_attack_request", ship_id, ship_type, target_id,
              target_type, position)
        self.flotte[ship_type][ship_id].target_to_attack(target_id,
                                                         target_type, position)

    def deplete_energy(self):
        """Consommation des ressources de la flotte de vaisseaux et des structures du joueur
            Compile la quantité d'énergie consommée que requiert les différents bâtiments et vaisseaux à la disposition du joueur.
            puis réaffecte la quantité d'énergie disponible au joueur.
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
        # Todo: Ajouter les variables bool docked et int consommation dans le modele vaisseau (2e sprint)

        self.ressources_total["Energie"] -= AlwaysInt(
            (conso_vaisseaux + conso_structures + self.consommation_joueur))

    def get_etoile_by_id(self, etoile_id: str) -> Etoile | None:
        """Renvoie l'étoile correspondant à l'id donné.

        :param etoile_id: l'id de l'étoile
        :return: l'étoile correspondant à l'id
        """
        for i in self.etoiles_controlees:
            if i.id == etoile_id:
                return i
        return None


class AI(Joueur):
    """Classe de l'AI.

    L'AI est le personnage non-joueur qui joue le jeu.
    """

    def __init__(self, nom: str,
                 etoile_mere: Etoile, couleur: str, command_queue) -> None:
        """Initialise l'AI.

        :param nom: le nom de l'AI
        :param etoile_mere: l'etoile mere de l'AI
        :param couleur: la couleur de l'AI
        """
        Joueur.__init__(self, nom, etoile_mere, couleur, command_queue)
        self.cooldownmax: int = 1000
        """Cooldown max de l'AI avant son prochain vaisseau."""
        self.cooldown: int = 20
        """Cooldown en cours de l'AI avant son prochain vaisseau."""

    def tick(self) -> None:
        pass
