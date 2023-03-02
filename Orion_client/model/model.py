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
from Orion_client.model.ships import Ship, Cargo, Fighter
from Orion_client.model.space_object import Wormhole, Star


class Model:
    """Classe du modèle.

    Le modèle contient les données du jeu.
    """
    def __init__(self, joueurs):
        """Initialise le modèle.

        :param joueurs: les joueurs du jeu
        """
        self.largeur: int = 9000
        self.hauteur:int = 9000
        self.nb_etoiles:int = int((self.hauteur * self.largeur) / 500000)
        self.joueurs: dict = {}
        self.actions_a_faire: dict = {}
        self.etoiles: list = []
        self.trou_de_vers : list = []
        self.cadre_courant = None  # TODO: type
        self.creeretoiles(joueurs, 1)
        nb_trou: int = int((self.hauteur * self.largeur) / 5000000)
        self.creer_troudevers(nb_trou)

    def creer_troudevers(self, n : int) -> None:
        """Crée des trous de vers.

        Créé n trous de vers aléatoirement dans le modèle.
        Les trous de vers sont des portes de vers. Ils sont créés en deux points
        aléatoires groupés en paires. Les trous de vers sont ajoutés à la liste
        des trous de vers du modèle.

        :param n: le nombre de trous de vers à créer"""
        bordure : int = 10
        for i in range(n):
            x1 = randrange(self.largeur - (2 * bordure)) + bordure
            y1 = randrange(self.hauteur - (2 * bordure)) + bordure
            x2 = randrange(self.largeur - (2 * bordure)) + bordure
            y2 = randrange(self.hauteur - (2 * bordure)) + bordure
            self.trou_de_vers.append(Wormhole(x1, y1, x2, y2))

    def creeretoiles(self, joueurs: dict, ias: int = 0):
        """Crée des étoiles, d'une certaine couleur dependant du joueur.

        Créé des étoiles aléatoirement dans le modèle dependant du nombre
        d'étoiles du modèle. Les étoiles sont ajoutées à la liste des étoiles
        du modèle et retirée du compteur des étoiles à créer.

        :param joueurs: les joueurs du jeu
        :param ias: le nombre d'AI à créer
        """
        bordure = 10
        for i in range(self.nb_etoiles):
            x = randrange(self.largeur - (2 * bordure)) + bordure
            y = randrange(self.hauteur - (2 * bordure)) + bordure
            self.etoiles.append(Star(self, x, y))
        np = len(joueurs) + ias
        etoile_occupee = []
        while np:
            p = choice(self.etoiles)
            if p not in etoile_occupee:
                etoile_occupee.append(p)
                self.etoiles.remove(p)
                np -= 1

        couleurs = ["red", "blue", "lightgreen", "yellow",
                    "lightblue", "pink", "gold", "purple"]
        for i in joueurs:
            etoile = etoile_occupee.pop(0)
            self.joueurs[i] = Player(self, i, etoile, couleurs.pop(0))
            x = etoile.x
            y = etoile.y
            dist = 500
            for e in range(5):
                x1 = randrange(x - dist, x + dist)
                y1 = randrange(y - dist, y + dist)
                self.etoiles.append(Star(self, x1, y1))

        # AI- creation des ias
        couleursia = ["orange", "green", "cyan",
                      "SeaGreen1", "turquoise1", "firebrick1"]
        for i in range(ias):
            self.joueurs["IA_" + str(i)] = AI(self, "IA_" + str(i),
                                              etoile_occupee.pop(0),
                                              couleursia.pop(0))

    def jouer_prochain_coup(self, cadre):
        """Joue le prochain coup pour chaque objet.

        Joue le prochain coup pour chaque objet du modèle. Ils y vont dans cette ordre
        : joueur, trou de vers.

        :param cadre: le cadre à jouer
        """

        #  NE PAS TOUCHER LES LIGNES SUIVANTES  #################
        self.cadre_courant = cadre

        # insertion de la prochaine action demandée par le joueur
        if cadre in self.actions_a_faire:
            for i in self.actions_a_faire[cadre]:
                self.joueurs[i[0]].action_from_server(i[1], i[2])
                """
                i a la forme suivante [nomjoueur, action, [arguments]
                alors self.joueurs[i[0]] -> trouve l'objet représentant le joueur de ce nom
                """
            del self.actions_a_faire[cadre]
        # FIN DE L'INTERDICTION #################################

        for i in self.joueurs:
            self.joueurs[i].jouer_prochain_coup()

        for i in self.trou_de_vers:
            i.jouer_prochain_coup()

    def ajouter_actions_a_faire(self, actionsrecues: list, frame: int):
        """Ajoute les actions reçue dans la liste des actions à faire
         si et seulement si le cadre est plus petit que le cadre courant.

        :param actionsrecues: la liste des actions reçues du serveur
        """
        for i in actionsrecues:
            cadrecle = i[0]
            if cadrecle:
                if (frame - 1) > int(cadrecle):
                    print("PEUX PASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
                action = literal_eval(i[1])

                if cadrecle not in self.actions_a_faire.keys():
                    self.actions_a_faire[cadrecle] = action
                else:
                    self.actions_a_faire[cadrecle].append(action)

                print("actions à faire", self.actions_a_faire)


class Player:
    """Classe du joueur.

    Le joueur est le personnage qui joue le jeu.
    Il possede une flotte de vaisseaux, une liste d'etoiles controlees et une
    liste d'actions.
    """
    def __init__(self, parent: Model, nom: str,
                 etoilemere: Star, couleur: str):
        """Initialise le joueur.

        :param parent: le jeu auquel le joueur appartient
        :param nom: le nom du joueur
        :param etoilemere: l'etoile mere du joueur
        :param couleur: la couleur du joueur
        """
        self.consommationJoueur = AlwaysInt(10)
        self.energie = AlwaysInt(10000)
        self.id : str = get_prochain_id()
        self.parent = parent
        self.nom = nom
        self.etoilemere = etoilemere
        self.etoilemere.proprietaire = self.nom
        self.couleur = couleur
        self.log: list = []
        """Liste des actions du joueur."""
        self.etoilescontrolees: list = [etoilemere]
        """Liste des etoiles controlees par le joueur."""

        self.flotte: dict[str, list[Ship] | Ship] = {}
        """Flotte du joueur."""

    def get_star_by_id(self, id: str):
        for i in self.etoilescontrolees:
            if i.id == id:
                return i
        return None

    def jouer_prochain_coup(self):
        """Fonction de jeu du joueur pour un tour.
        """
        for i in self.flotte:
            self.flotte[i].tick()

    def action_from_server(self, funct: str, args: list):
        """Fonction de jeu du joueur pour un tour.
        """
        getattr(self, funct)(*args)

    def construct_fighter(self, star_id: str):
        """Fonction de jeu du joueur pour un tour.
        """
        pos = self.get_star_by_id(star_id).pos
        fighter = Fighter(pos, self.id)
        self.flotte[fighter.id] = fighter

    def move_fighter(self, ship_id: str, pos: tuple):
        """Fonction de jeu du joueur pour un tour.
        """
        self.flotte[ship_id].position_cible = pos




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
        self.energie -= AlwaysInt((self.consoVaisseau + self.consoStructure + self.consommationJoueur))


class AI(Player):
    """Classe de l'AI.

    L'AI est le personnage non-joueur qui joue le jeu.
    """
    def __init__(self, parent: Model, nom: str,
                 etoilemere: Star, couleur: str) -> None:
        """Initialise l'AI.

        :param parent: le jeu auquel l'AI appartient
        :param nom: le nom de l'AI
        :param etoilemere: l'etoile mere de l'AI
        :param couleur: la couleur de l'AI
        """
        Player.__init__(self, parent, nom, etoilemere, couleur)
        self.cooldownmax: int = 1000
        """Cooldown max de l'AI avant son prochain vaisseau."""
        self.cooldown: int = 20
        """Cooldown en cours de l'AI avant son prochain vaisseau."""

    def jouer_prochain_coup(self) -> None:
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
            self.nb_humains *= AlwaysInt((100 + self.pourcentBonus) + (self.totalNourriture / self.nb_humains))
        else:  # si la population de la planete est attaquée
            self.nb_humains = AlwaysInt(self.nb_humains * ((100 - self.pourcentBonus) / 100))

        # Si le retour est 0 ou moins
        # d'un chiffre acceptable pour la subsistance de la planète (à déterminer),
        # elle peut alors être conquise.




