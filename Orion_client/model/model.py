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
from Orion_client.model.building import ResearchCenter, PowerPlant
from Orion_client.model.ressource import Ressource
from Orion_client.model.space_object import Wormhole, Star


class Model:
    """Classe du modèle.

    Le modèle contient les données du jeu.
    """

    def __init__(self, parent, joueurs):
        """Initialise le modèle.

        :param parent: le jeu auquel le modèle appartient
        :param joueurs: les joueurs du jeu
        """
        self.parent = parent
        self.largeur: int = 9000
        self.hauteur: int = 9000
        self.nb_etoiles: int = int((self.hauteur * self.largeur) / 500000)
        self.joueurs: dict = {}
        self.actions_a_faire: dict = {}
        self.etoiles: list = []
        self.trou_de_vers: list = []
        self.cadre_courant = None  # TODO: type
        self.creeretoiles(joueurs, 1)
        nb_trou: int = int((self.hauteur * self.largeur) / 5000000)
        self.creer_troudevers(nb_trou)

    def creer_troudevers(self, n: int) -> None:
        """Crée des trous de vers.

        Créé n trous de vers aléatoirement dans le modèle.
        Les trous de vers sont des portes de vers. Ils sont créés en deux points
        aléatoires groupés en paires. Les trous de vers sont ajoutés à la liste
        des trous de vers du modèle.

        :param n: le nombre de trous de vers à créer"""
        bordure: int = 10
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
                self.joueurs[i[0]].actions[i[1]](i[2])
                """
                i a la forme suivante [nomjoueur, action, [arguments]
                alors self.joueurs[i[0]] -> trouve l'objet représentant le joueur de ce nom
                """
            del self.actions_a_faire[cadre]
        # FIN DE L'INTERDICTION #################################

        # demander aux objets de jouer leur prochain coup
        # aux joueurs en premier
        for i in self.joueurs:
            self.joueurs[i].jouer_prochain_coup()

        # NOTE si le modele (qui représente l'univers !!! )
        #      fait des actions - on les activera ici...
        for i in self.trou_de_vers:
            i.jouer_prochain_coup()

    def ajouter_actions_a_faire(self, actionsrecues: list):
        """Ajoute les actions reçue dans la liste des actions à faire
         si et seulement si le cadre est plus petit que le cadre courant.

        :param actionsrecues: la liste des actions reçues du serveur
        """
        cadrecle = None
        for i in actionsrecues:
            cadrecle = i[0]
            if cadrecle:
                if (self.parent.cadrejeu - 1) > int(cadrecle):
                    print("PEUX PASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
                action = literal_eval(i[1])

                if cadrecle not in self.actions_a_faire.keys():
                    self.actions_a_faire[cadrecle] = action
                else:
                    self.actions_a_faire[cadrecle].append(action)


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
        self.id: str = get_prochain_id()
        self.parent = parent
        self.nom = nom
        self.etoilemere = etoilemere
        self.etoilemere.transit = True
        self.etoilemere.proprietaire = self.nom
        self.couleur = couleur
        self.log: list = []
        self.ressources = Ressource(metal=500, beton=500, energie=1000, nourriture=500)
        """Liste des actions du joueur."""
        self.etoilescontrolees: list = [etoilemere]
        """Liste des etoiles controlees par le joueur."""

        self.flotte = {"Vaisseau": {},
                       "Cargo": {}}
        """Flotte du joueur."""

        self.actions = {}

    def jouer_prochain_coup(self):
        """Fonction de jeu du joueur pour un tour.
        """
        self.ressources_cumul()
        print()
        print(self.ressources)
        pass

    def ressources_cumul(self):
        for e in self.etoilescontrolees:
            print(e.buildinglist[0].output)

            if e.transit:
                planetRes: Ressource = e.output
                for b in e.buildinglist:
                    if isinstance(b, PowerPlant):
                        planetRes += b.output
                    elif isinstance(b, ResearchCenter):
                        continue
                    else:
                        planetRes *= b.output
                self.ressources += planetRes
        pass


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
