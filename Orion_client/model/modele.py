"""Modartefact_id=Nonede donnees du jeu
Ce module contient les classes qui representent les objets du jeu ainsi
que le modèle de base du jeu.
"""
from __future__ import annotations

import json
import os
from ast import literal_eval
from random import randrange, choice
from typing import Generator

from Orion_client.interface import IModel, IJoueur
from Orion_client.helpers.CommandQueues import JoueurQueue, ModelQueue
from Orion_client.helpers.helper import AlwaysInt, StringTypes, \
    get_prochain_id, MessageManager
from Orion_client.model.building import *

from Orion_client.model import ships
from Orion_client.model.building import Building
from Orion_client.model.ressource import Ressource
from Orion_client.model.ships import Ship, Flotte
from Orion_client.model.space_object import TrouDeVers, Etoile, Artefact
import math

from Orion_client.model.building import PowerPlant, ResearchCenter, ConcreteFactory, Farm, Mine


import math

class Modele(IModel):
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
        self.artefacts: list = []
        self.joueurs: dict = {}

        self.local_queue = ModelQueue()
        self.log: dict = {}

        self.science = json.loads(open("data/json/sciences.json").read())

        self.message_manager = MessageManager()
        self.message_manager.add_message(f"Serveur : Bienvenue dans Orion, "
                                         f"{self.controller_username} !")

        with open("./data/text/star.csv", "r") as star_name_csv:
            star_name_csv = star_name_csv.read().split("\n")

        self.creer_trou_de_vers(int((self.hauteur * self.largeur) / 5000000))
        self.creer_etoiles(int((self.hauteur * self.largeur) / 500000),
                           star_name_csv)
        self.creer_artefacts(int((self.hauteur * self.largeur) / 750000))
        self.creer_joueurs(joueurs, star_name_csv)
        self.creer_ias()

    def receive_message(self, message):
        """Reçoit un message du serveur et l'ajoute à la queue des messages.
        :param message: Le message reçu
        """
        self.message_manager.add_message(message)

    def get_objects_in_view(self, x1, x2, y1, y2):
        return {
            StringTypes.VAISSEAU.value: self.get_vaisseau_in_view(x1, x2, y1, y2),
            StringTypes.ETOILE.value: self.get_etoiles_in_view(x1, x2, y1, y2),
            StringTypes.TROUDEVERS.value: self.get_porte_de_vers_in_view(x1, x2, y1, y2),
            StringTypes.ARTEFACT.value: self.get_artefacts_in_view(x1, x2, y1, y2)
        }

    def get_etoiles_in_view(self, x1, y1, x2, y2) \
            -> Generator[Etoile, None, None]:
        for etoile in self.etoiles:
            if x1 <= etoile.x <= x2 and y1 <= etoile.y <= y2:
                yield etoile
        for username in self.joueurs.keys():
            for etoile in self.joueurs[username].etoiles_controlees:
                if x1 <= etoile.x <= x2 and y1 <= etoile.y <= y2:
                    yield etoile

    def get_artefacts_in_view(self, x1, y1, x2, y2):
        # \
        #     -> Generator[Artefact, None, None]:
        for artefact in self.artefacts:
            if x1 <= artefact.x <= x2 and y1 <= artefact.y <= y2:
                yield artefact

    def get_porte_de_vers_in_view(self, x1, y1, x2, y2):
        for trou in self.trou_de_vers:
            for porte in trou.portes:
                if x1 <= porte.x <= x2 and y1 <= porte.y <= y2:
                    yield porte

    def is_star_in_view(self, _id, x1, y1, x2, y2):
        star = self.get_object(_id, StringTypes.ETOILE)
        if star:
            return x1 <= star.x <= x2 and y1 <= star.y <= y2
        return False

    def get_vaisseau_in_view(self, x1, y1, x2, y2):
        for username in self.joueurs.keys():
            for key in self.joueurs[username].flotte.keys():
                for id, vaisseau in self.joueurs[username].flotte[key].items():
                    x = vaisseau.position[0]
                    y = vaisseau.position[1]
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        yield vaisseau

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
                planet.couleur = "white"
                planet.needs_refresh = True
            else:
                self.etoiles.remove(planet)
                self.joueurs[new_owner].conquer_planet(planet)
                planet.needs_refresh = True

    def add_artefact_to_player(self, artefact_id: str, owner: None):
        """Ajouter un artéfact au joueur en sa possession."""
        artefact = self.get_object(artefact_id, StringTypes.ARTEFACT)
        self.joueurs[owner].artefacte_reclames.add(artefact_id)
        self.joueurs[owner].claim_artefact(artefact)

    def target_change_request(self, ship_informations: dict, target: dict):
        """Demande de changement de cible d'un vaisseau.
        """
        player_ship = self.get_object(ship_informations["id"],
                                      ship_informations["type"])
        print("print de target_change_request", ship_informations, target)
        new_pos = target["pos"]
        if "id" in target:
            new_target = self.get_object(target["id"], target["type"])
            print("Quel est le target:", target, "new target:", new_target)
            player_ship.target_change(new_pos, new_target)
        else:
            player_ship.target_change(new_pos)

    def get_object(self, object_id, object_type=None,
                   owner=None) -> None | Ship | Flotte | TrouDeVers | Etoile | Artefact:
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

            elif object_type in StringTypes.artefact_type():
                temp_object = self.__get_artefacte(object_id)

        else:
            temp_object = self.__get_ship(object_id, owner=owner)
            if not temp_object:
                temp_object = self.__get_etoile(object_id)

        if not temp_object:
            print(f"Object not found in get_object with parameter : "
                  f"{object_id}, {object_type}, {owner}")
        return temp_object

    def __get_artefacte(self, artefact_id):
        """Retourne un artefact"""
        for artefact in self.artefacts:
            if artefact.id == artefact_id:
                return artefact

    def __get_etoile(self, etoile_id):
        """Retourne une étoile.
          :param etoile_id: l'id de étoile.
          :ivar etoile: Recherche de l'id de l'étoile
          :ivar joueur: Recherche du nom du joueur
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
                            # todo : remove this mess

        self.cadre = cadre
        if cadre in self.log:
            for i in self.log[cadre]:
                if i[0] != "model":
                    cible = self.joueurs[i[0]]
                else:
                    cible = self
                funct = i[1]
                args = i[2]
                funct = getattr(cible, funct)
                funct(*args)

            del self.log[cadre]

        for i in self.etoiles:
            i.tick()

        for i in self.joueurs:
            self.joueurs[i].tick()

        for i in self.trou_de_vers:
            i.tick()

        for i in self.artefacts:
            i.tick()

        # Command queues
        self.execute_commands(self.local_queue)
        for i in self.joueurs:
            self.joueurs[i].execute_commands(self.joueurs[i].local_queue)

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

    def creer_etoiles(self, nb_etoiles: int, star_name_csv):
        """Crée des étoiles, d'une certaine couleur dépendant du joueur.
        :param nb_etoiles: le nombre d'étoiles à créer.
        :param star_name_csv: le nom du fichier csv contenant
        les noms des étoiles.
        """
        bordure = 10
        self.etoiles = [
            Etoile(randrange(self.largeur - (2 * bordure)) + bordure,
                   randrange(self.hauteur - (2 * bordure)) + bordure,
                   self.local_queue, star_name_csv)
            for _ in range(nb_etoiles)]


    def creer_artefacts(self, nb_artefacts: int):
        """Crée les artéfacts au moment de générer le monde.
        :param nb_artefacts: Quantité d'Artéfact dans l'espace."""

        for _ in range(nb_artefacts):
            x1 = randrange(10, self.largeur - 10)
            y1 = randrange(10, self.hauteur - 10)
            self.artefacts.append(Artefact(x1, y1, self.local_queue, False))

    def creer_joueurs(self, joueurs: list, star_name_csv):
        """Créé les joueurs et leur attribue une etoile mère.
        :param joueurs: la liste des joueurs à créer
        :param star_name_csv: le nom du fichier csv contenant
        les noms des étoiles.
        """
        couleurs = ["red", "blue", "yellow", "orange"]
        etoiles_occupee = []
        for i in range(len(joueurs)):
            p = choice(self.etoiles)
            etoiles_occupee.append(p)
            self.etoiles.remove(p)

        for i, joueur in enumerate(joueurs):
            if not couleurs:
                couleurs = ["red", "blue", "yellow", "orange"]
            etoile = etoiles_occupee[i]
            self.joueurs[joueur] = Joueur(joueur, etoile, couleurs.pop(0),
                                          self.local_queue,
                                          self.controller_username,
                                          self.science)
            for e in range(5):
                self.etoiles.append(
                    Etoile(randrange(etoile.x - 500, etoile.x + 500),
                           randrange(etoile.y - 500, etoile.y + 500),
                           self.local_queue, star_name_csv)
                )

    def creer_ias(self, ias: int = 0):
        """Créer les IAs et leur attribue une etoile mère.
        :param ias: le nombre d'IA à créer
        """
        couleurs = ["red", "blue", "yellow", "orange"]
        etoiles_occupee = []
        for i in range(ias):
            if not couleurs:
                couleurs = ["red", "blue", "yellow", "orange"]
            p = choice(self.etoiles)
            etoiles_occupee.append(p)
            self.etoiles.remove(p)
        for i in range(ias):
            self.joueurs[f"IA_{i}"] = AI(f"IA_{i}", etoiles_occupee.pop(0),
                                         couleurs.pop(0),
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

    def get_player_stars(self):
        """Récupère les étoiles contrôlées par le joueur
        :return: Une liste d'étoiles"""
        stars = []
        for star in self.joueurs.keys():
            for j in self.joueurs[star].etoiles_controlees:
                stars.append(j)
        return stars


class Joueur(IJoueur):
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
                 local_queue,
                 controller_owner: str, science):
        """Initialise le joueur.
        :param nom: le nom du joueur
        :param etoile_mere: l'etoile mere du joueur
        :param couleur: la couleur du joueur
        """
        self.id: str = get_prochain_id()
        """L'id du joueur."""
        self.nom = nom
        self.etoile_mere = etoile_mere
        print("pos_mere", self.etoile_mere.position)
        self.etoile_mere.transit = True
        self.etoile_mere.buildinglist = [Farm(), Mine(), PowerPlant()]
        self.etoile_mere.proprietaire = self.nom
        """Le nom du joueur."""
        self.is_controller_owner = controller_owner == nom
        self.couleur = couleur
        """La couleur du joueur."""
        self.flotte: Flotte = Flotte()
        """Flotte du joueur."""
        self.etoiles_controlees: list = [etoile_mere]
        """Liste des etoiles controlees par le joueur."""
        self.artefacte_reclames: list = []
        """Artefact réclamées par le joueur"""
        self.consommation_energie_joueur = AlwaysInt(10)
        """Ressources totales du joueur."""

        self.local_queue = local_queue
        """Queue de commandes du modèle au controller."""
        self.player_local_queue = JoueurQueue()
        self.sciences_status = {}


        science = json.loads(open("data/json/sciences.json").read())

        for key in science.keys():
            temp_science = key
        for key2 in science[key].keys():
            self.sciences_status[temp_science] =[science[key]["price"], science[key]["bonus"]]

        """Sciences du joueur."""

        self.ressources = Ressource(metal=100, beton=100, energie=100,
                                    nourriture=100,
                                    science=0)
        """L'etoile mere du joueur."""
        self.etoile_mere.couleur = couleur
        self.etoile_mere.proprietaire = self.nom

        self.recently_lost_ships_id = []
        self.cadre_consommation = 0

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

    def claim_artefact(self, artefact: Artefact):
        """Rend un artéfact inaccessible à d'autres joueurs."""
        artefact.claimed = True
        self.artefacte_reclames.append(artefact)

    def construct_ship(self, planet_id, type_ship):
        """
        Déclenche la construction d'un vaisseau sur une planète dépendant
        du type de vaisseau demandé.
        :param planet_id: l'id de la planète sur laquelle construire
        le vaisseau
        :param type_ship: le type de vaisseau à construire
        """
        pos = self.get_etoile_by_id(planet_id).position
        print("pos", pos)
        ship = getattr(ships, type_ship.capitalize())(
            pos, self.nom, self.local_queue, self.player_local_queue
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

    def construct_building_request(self, etoile_id: str, type_building: str,
                                   list_position: int):
        """Fonction que est reçu du serveur depuis la vue du jeu.
        Elle s'assure que la construction d'un vaisseau est possible et
        la déclenche si elle l'est."""
        # make a switch case
        print(list_position)

        etoile = self.get_etoile_by_id(etoile_id)

        match type_building:
            case "mine":
                Mine.build_request(self.ressources, etoile.buildinglist, list_position)
            case "farm":
                Farm.build_request(self.ressources, etoile.buildinglist, list_position)
            case "concretefactory":
                ConcreteFactory.build_request(self.ressources, etoile.buildinglist, list_position)
            case "powerplant":
                PowerPlant.build_request(self.ressources, etoile.buildinglist, list_position)
            case "reserchcenter":
                ResearchCenter.build_request(self.ressources, etoile.buildinglist, list_position)
            case _:
                print("pas asser de ressources")

        print(etoile.buildinglist)


    def deplete_energy(self):
        """
        Consommation des ressources de la flotte de vaisseaux et
        des structures du joueur.
        Compile la quantité d'énergie consommée que requiert les différents
        bâtiments et vaisseaux à la disposition du joueur puis réaffecte la
        quantité d'énergie disponible au joueur.
        :ivar conso_structures: Consommation d'énergie par chaque bâtiment sur une planète contrôlée par l'empire.
        :ivar conso_vaisseaux: Consommation d'énergie par chaque vaisseau (s'il n'est pas docké) sur une planète contrôlée par l'empire.
        """
        conso_structures: int = 0
        conso_vaisseaux: int = 0
        """Consommation d'énergie des structures du joueur"""
        for e in self.etoiles_controlees:
            for b in e.buildinglist:
                if isinstance(b, Building):
                    conso_structures += b.consumption

        """Consommation des vaisseaux de la flotte du joueur."""
        for typeVaisseau, dictVaisseau in self.flotte.items():
            for idVaisseau, vaisseau in self.flotte[typeVaisseau].items():
                if not vaisseau.docked:
                    conso_vaisseaux += vaisseau.consommation

        # Todo: Ajouter les variables bool docked et int consommation
        #  dans le modele vaisseau (2e sprint)

        self.ressources["energie"] -= AlwaysInt(
            (conso_vaisseaux + conso_structures +
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
        """Fonction de jeu du joueur pour un tour."""
        self.cadre_consommation += 1

        for etoile in self.etoiles_controlees:
            etoile.tick()

        for type_ship in self.flotte.keys():
            for ship in self.flotte[type_ship]:
                self.flotte[type_ship][ship].tick()

        self.ressources_cumul()
        self.deplete_energy()
        if self.cadre_consommation % 60 == 0:
            self.increment_pop()
            self.cadre_consommation = 0

    def ressources_cumul(self):
        """Fonction pour cumuler les ressources du joueur
        de chaque planète connectée au système de transit."""
        for e in self.etoiles_controlees:
            if e.transit:
                planet_res: Ressource = Ressource()
                for key in e.output:
                    planet_res[key] = e.output[key]

                for b in e.buildinglist:
                    if isinstance(b, PowerPlant):
                        planet_res = planet_res + b.output
                    elif isinstance(b, ResearchCenter):
                        continue
                    else:
                        for key in planet_res:
                            planet_res[key] = planet_res[key] * b.output[key]

                self.ressources += planet_res

    def increment_pop(self):
        """Met à niveau la population d'une planète selon
        la quantité de nourriture disponible à travers
        toutes les étoiles constrôlées dans l'empire d'un joueur.
        :ivar tot_population: Population totale de l'empire.
        :ivar cpt_transit: Quantité de planètes connectées au système de transit.
        :ivar nourriture_apres_conso: Quantité de nourriture à la disposition de l'empire
                                      après avoire nourri sa population.
        """
        tot_population: int = 0
        cpt_transit = 0
        """passer a travers les etoiles"""
        for p in self.etoiles_controlees:
            if p.transit:
                tot_population += p.population
                cpt_transit += 1

        """Consommation de nourriture par tick (server % 30)"""
        self.ressources["nourriture"] -= tot_population

        nourriture_apres_conso = self.ressources["nourriture"]
        nourriture_apres_conso *= .15
        nourriture_apres_conso /= cpt_transit

        for c in self.etoiles_controlees:
            if c.transit:
                c.population += math.floor(nourriture_apres_conso)
            else:
                c.population = AlwaysInt(c.population * .90)
            if c.population <= 0:
                c.population = 0

            # TODO : tester que la reduction par pourcentage permet une
            #  conquete facile



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
