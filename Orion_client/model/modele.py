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
from Orion_client.model.ships import Ship, Transport, Militaire, Reconnaissance
from Orion_client.model.space_object import TrouDeVers, Etoile


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
            self.joueurs[joueur] = Joueur(joueur, etoile, couleurs.pop(0), self.command_queue)
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
                                         couleurs_ia.pop(0), self.command_queue)

    def tick(self, cadre):
        """Joue le prochain coup pour chaque objet.

        :param cadre: le cadre à jouer (frame)
        """

        #  NE PAS TOUCHER LES LIGNES SUIVANTES  #################
        # insertion de la prochaine action demandée par le joueur
        if cadre in self.log:
            for i in self.log[cadre]:
                print("action recue", i)
                # Ici, if i[0] == model j'envoie l'action au model
                # Sinon, je l'envoie au joueur
                if i:
                    if i[0] == "model":
                        getattr(self, i[1])(i[2])
                    else:
                        self.joueurs[i[0]].action_from_server(i[1], i[2])
                """
                i a la forme suivante [nomjoueur, action, [arguments]
                alors self.joueurs[i[0]] -> trouve l'objet représentant le joueur de ce nom
                """
            del self.log[cadre]
        # FIN DE L'INTERDICTION #################################

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

        self.flotte: dict[str, list[Ship] | Ship] = {}
        """Flotte du joueur."""

    def tick(self):
        """Fonction de jeu du joueur pour un tour.
        """
        for i in self.flotte:
            self.flotte[i].tick()

    def action_from_server(self, funct: str, args: list):
        """Fonction qui active une action du joueur reçue du serveur en
        fonction de la fonction et des arguments envoyés.

        :param funct: la fonction à activer
        :param args: les arguments de la fonction

        """
        getattr(self, funct)(*args)

    def construct_ship_request(self, planet_id: str, type_ship: str):
        """Fonction que est reçu du serveur. Elle s'assure que la construction
        d'un vaisseau est possible et la déclenche si elle l'est."""
        has_enough_ressources : bool = True # Pour debug
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
            self.flotte[ship.id] = ship

    def ship_target_change_request(self, ship_id: str, pos: tuple):
        """Fonction qui permet de déplacer un vaisseau spécifiquement.

        :param ship_id: l'id du vaisseau à déplacer
        :param pos: la position cible du vaisseau
        """
        self.flotte[ship_id].target_change(pos)

    def deplete_energy(self, list_vaisseau: list, list_structure: list):
        """Consommation des ressources de la flotte de vaisseaux et des structures du joueur
        :param list_vaisseau: Liste des vaisseaux du joueur
        :param list_structure: Liste des structure du joueur à sa disposition

        :return: quantité total d'énergie consommée.
            """
        self.consoVaisseau = 0
        self.consoStructure = 0

        for vaisseau in list_vaisseau:
            if vaisseau.docked:
                self.consoVaisseau += vaisseau.consommation / 2
            else:
                self.consoVaisseau += vaisseau.consommation

        for structure in list_structure:
            self.consoStructure += structure.consommation
        # TODO Ajuster la méthode si on doit s'en servir
        # TODO comme getter (return) ou affectation directe à la classe Joueur
        self.energie -= AlwaysInt((self.consoVaisseau + self.consoStructure
                                   + self.consommation_joueur))

    def get_etoile_by_id(self, etoile_id: str) -> Etoile | None:
        """Renvoie l'étoile correspondant à l'id donné.

        :param etoile_id: l'id de l'étoile
        :return: l'étoile correspondant à l'id
        """
        for i in self.etoiles_controlees:
            if i.id == etoile_id:
                return i
        return None

    def get_all_static_ships_positions(self):
        """Renvoie la position de tous les vaisseaux statiques du joueur.
        """
        pos = []
        for i in self.flotte:
            if self.flotte[i].is_static():
                pos.append(self.flotte[i].position)
        return pos


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


class Population:
    """ Population de la planète découverte
    """

    def __init__(self, pop, totalNourriture, pourcentBonus):
        """
        :param pop: Initialise la quantité d'habitants sur la planètes.
        :param totalNourriture: Initialise la quantité de nourriture disponible.
        :param pourcentBonus: taux de croissance de la population lorsqu'elle prospère
                ou taux de perte de vie humaine si elle est attaquée


        """
        self.nb_humains = AlwaysInt(pop)
        self.is_under_siege = False
        self.totalNourriture = AlwaysInt(totalNourriture)
        self.pourcentBonus = pourcentBonus
        # pourcentBonus pourrait être un boni donné à la découverte de l'étoile
        # ou selon un niveau de défense (à déterminer)

    def increment_pop(self, isUnderSiege: bool):
        """ Modifie la quantité de la population de la planète selon son état.
            Appelée à des intervalles spécifiques ou dès que la planète est attaquée

            :param isUnderSiege: Booléen qui détermine si la planète est présentement attaquée.
            :return: quantité d'humains vivant sur la planète.
        """

        #   Version 1, incluant une condition sur la quantité d'humains
        #   if not self.nb_humains:
        #       return 0
        #   else:

        self.is_under_siege = isUnderSiege
        # déterminer au moment de l'appel de la méthode si la population est sous-attaque.
        if not self.is_under_siege:
            self.nb_humains *= AlwaysInt((100 + self.pourcentBonus) + (
                        self.totalNourriture / self.nb_humains))
        else:  # si la population de la planete est attaquée
            self.nb_humains = AlwaysInt(
                self.nb_humains * ((100 - self.pourcentBonus) / 100))

        # Si le retour est 0 ou moins
        # d'un chiffre acceptable pour la subsistance de la planète (à déterminer),
        # elle peut alors être conquise.
