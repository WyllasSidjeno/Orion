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

import random
import ast

from _distutils_hack import override

from id import *
from helper import Helper as hlp


class Porte_de_vers():
    """Classe representant une porte de vers.

    Une porte de vers est une partie d'un trou de vers. Il s'agit de
    la partie visible de l'hyper-espace. Elle est representee par un
    cercle qui se dilate et se contracte."""

    def __init__(self, parent: Trou_de_vers, x: int, y: int,
                 couleur: str, taille: int) -> None:
        """Constructeur de la classe Porte_de_vers. todo : link

        :param parent: le trou de vers auquel la porte appartient
        :param x: coordonnee x du centre de la porte
        :param y: coordonnee y du centre de la porte
        :param couleur: la couleur de la porte
        :param taille: la taille de la porte
        """
        self.parent = parent
        self.id = get_prochain_id()
        self.x = x
        self.y = y
        self.pulsemax = taille
        self.pulse = random.randrange(self.pulsemax)
        self.couleur = couleur

    def jouer_prochain_coup(self) -> None:
        """Incremente le compteur de pulsation de la porte ou le remet
        a zero si il atteint la taille maximale."""
        self.pulse += 1
        if self.pulse >= self.pulsemax:
            self.pulse = 0


class Trou_de_vers():
    """Classe representant un trou de vers.

    Un trou de vers est un lien entre deux systemes stellaires. Il
    permet de voyager d'un systeme a l'autre en passant par l'hyper-espace
    via une porte de vers vers une autre porte de vers. todo: link"""

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Constructeur de la classe Trou_de_vers.

        :param x1: coordonnee x de la premiere porte de vers
        :param y1: coordonnee y de la premiere porte de vers
        :param x2: coordonnee x de la deuxieme porte de vers
        :param y2: coordonnee y de la deuxieme porte de vers
        """
        self.id = get_prochain_id()
        taille = random.randrange(6, 20)
        self.porte_a = Porte_de_vers(self, x1, y1, "red", taille)
        self.porte_b = Porte_de_vers(self, x2, y2, "orange", taille)
        self.liste_transit = []  # pour mettre les vaisseaux qui ne sont plus dans l'espace mais maintenant l'hyper-espace

    def jouer_prochain_coup(self) -> None:
        """Envoie le signal de jouer_prochain_coup
        aux deux portes de vers du trou de vers."""
        self.porte_a.jouer_prochain_coup()
        self.porte_b.jouer_prochain_coup()


class Etoile():
    """Classe representant une etoile.

    Une etoile est un objet celeste qui contient des ressources et
    potentiellement un propriétaire."""

    def __init__(self, parent: Modele, x: int, y: int) -> None:
        """Constructeur de la classe Etoile.

        :param parent: le modele auquel l'etoile appartient
        :param x: coordonnee x de l'etoile
        :param y: coordonnee y de l'etoile
        """
        self.id: str = get_prochain_id()
        self.parent = parent
        self.proprietaire: str = ""
        self.x = x
        self.y = y
        self.taille = random.randrange(4, 8)
        self.ressources = {"metal": 1000,
                           "energie": 10000,
                           "existentielle": 100}


class Vaisseau():
    """Classe representant un vaisseau.

    Un vaisseau est un objet qui peut se deplacer dans l'espace une fois
    une location cible est definie."""

    def __init__(self, parent: Joueur, nom: str, x: int, y: int) -> None:
        """"
        Constructeur de la classe Vaisseau.

        :param parent: le modele auquel le vaisseau appartient
        :param nom: le nom du proprietaire du vaisseau
        :param x: coordonnee x du vaisseau
        :param y: coordonnee y du vaisseau
        """
        self.parent = parent
        self.id: str = get_prochain_id()
        self.proprietaire = nom
        self.x = x
        self.y = y
        self.espace_cargo: int = 0
        self.energie: int = 100
        self.taille: int = 5
        self.vitesse: int = 2
        self.cible: int | Porte_de_vers | Etoile = 0
        self.type_cible: str | None = None
        self.angle_cible: float = 0
        self.arriver: dict[str, Callable] = {"Etoile": self.arriver_etoile,
                                             "Porte_de_vers": self.arriver_porte}

    def jouer_prochain_coup(self, trouver_nouveau=0) \
            -> list[str, Etoile | Porte_de_vers]:
        """Fait avancer le vaisseau vers sa cible si elle existe,
        sinon il en cherche une nouvelle aleatoirement et la cible."""
        # todo: trouver_nouveau
        if self.cible != 0:
            return self.avancer()
        elif trouver_nouveau:
            cible = random.choice(self.parent.parent.etoiles)
            self.acquerir_cible(cible, "Etoile")

    def acquerir_cible(self, cible: Etoile | Porte_de_vers,
                       type_cible: str) -> None:  # todo: Verifier type cible
        """Acqueris une cible pour un vaisseau en changeant son type de cible,
        sa cible et son angle de cible.

        :param cible: la cible a acquerir
        :param type_cible: le type de la cible a acquerir
        """
        self.type_cible = type_cible
        self.cible = cible
        self.angle_cible: float = hlp.calcAngle(self.x, self.y,
                                                self.cible.x, self.cible.y)
        """L'angle de la cible est calcule par rapport a la position du vaisseau
        et de la cible."""

    def avancer(self) -> None:
        """Fait avancer le vaisseau vers sa cible."""  # todo:JM
        if self.cible != 0:
            x = self.cible.x
            y = self.cible.y

            self.x, self.y = hlp.getAngledPoint(
                self.angle_cible, self.vitesse, self.x, self.y)

            if hlp.calcDistance(self.x, self.y, x, y) <= self.vitesse:
                type_obj = type(self.cible).__name__
                rep = self.arriver[type_obj]()
                return rep

    def arriver_etoile(self) -> list[str, Etoile]:
        """Fonction d'arriver à l'etoile.

        Si le proprietaire de l'etoile est vide, le joueur devient propriétaire
        de l'etoile.
        Par la suite, la cible devient 0

        :return list of str and Etoile

        :return: une liste contenant le type de l'objet et l'objet lui-meme"""
        self.parent.log.append(
            ["Arrive:", self.parent.parent.cadre_courant, "Etoile", self.id,
             self.cible.id, self.cible.proprietaire])
        if not self.cible.proprietaire:
            self.cible.proprietaire = self.proprietaire
        cible = self.cible
        self.cible = 0
        return ["Etoile", cible]

    def arriver_porte(self) -> list[str, Porte_de_vers]:
        """Fonction d'arriver à la porte de vers.

        Lorsqu'arrive à la porte de vers, le vaisseau se téléporte à l'autre
        porte de vers de la même étoile, qui est liée à la porte de vers
        grace au trou de vers.
        Ensuite, la cible devient 0.

        :return list of str and Porte_de_vers
        """
        self.parent.log.append(
            ["Arrive:", self.parent.parent.cadre_courant, "Porte", self.id,
             self.cible.id, ])
        cible = self.cible
        trou = cible.parent
        if cible == trou.porte_a:
            self.x = trou.porte_b.x + random.randrange(6) + 2
            self.y = trou.porte_b.y
        elif cible == trou.porte_b:
            self.x = trou.porte_a.x - random.randrange(6) + 2
            self.y = trou.porte_a.y
        self.cible = 0
        return ["Porte_de_ver", cible]


class Cargo(Vaisseau):
    """Classe du vaisseau cargo.

    Le vaisseau cargo est un vaisseau qui peut transporter des ressources.
    """
    def __init__(self, parent: Joueur, nom: str, x: int, y: int) -> None:
        """Initialise le vaisseau cargo.

        :param parent: le joueur qui possede le vaisseau
        :param nom: le nom du vaisseau
        :param x: la position x du vaisseau
        :param y: la position y du vaisseau
        """
        Vaisseau.__init__(self, parent, nom, x, y)
        self.cargo : int = 1000
        self.energie : int = 500
        self.taille: int = 6
        self.vitesse: int = 1
        self.cible = 0 # todo : verifier si c'est necessaire
        self.ang = 0 # todo : verifier type (float?)


class Joueur():
    """Classe du joueur.

    Le joueur est le personnage qui joue le jeu.
    Il possede une flotte de vaisseaux, une liste d'etoiles controlees et une
    liste d'actions.
    """
    def __init__(self, parent: Modele, nom: str,
                 etoilemere: Etoile, couleur: str):
        """Initialise le joueur.

        :param parent: le jeu auquel le joueur appartient
        :param nom: le nom du joueur
        :param etoilemere: l'etoile mere du joueur
        :param couleur: la couleur du joueur
        """
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

        self.flotte = {"Vaisseau": {},
                       "Cargo": {}}
        """Flotte du joueur."""

        self.actions = {"creervaisseau": self.creervaisseau,
                        "ciblerflotte": self.ciblerflotte}
        """Liste des actions possible du joueur."""

        self.depletion_rate: int = 1
        """Taux de consommation de l'energie"""
        self.unlocked_puzzles: list = [bool]
        """Liste des enigmes deverouillees par le joueur"""
        self.ressources: dict = {} #à revoir

        # Quantité d'énergie de départ
        # conceptuellement
        self.energie = 100

    # Concept de consommation d'energie base sur la consommation de la flotte d'un joueur, n'est pas final
    # à décider si on utilise des listes ou dictionnaires pour la flotte de nos vaisseaux
    def deplete_energy(self):
        self.concept_flotteconcept_flotte = ["Vaisseau", "Cargo", "Recon"][self.flotte.keys()]
        self.consoEnergie = 0
        # type_vaisseau = ["Vaisseau", "Cargo", "Recon"]
        totalenergy = 0
        # for i in self.flotte.keys().__getattribute__("Vaisseau"):
        i = 0
        j = 0
        for typeVaisseau in self.concept_flotte[j][i]:
            for idVaisseau in self.concept_flotte[j][i]:
               self.consoEnergie += self.concept_flotte[j][i].energie

        self.energie -= (self.consoEnergie * self.depletion_rate)




    def creervaisseau(self, params: list) -> Vaisseau:
        """Fonction de creation d'un vaisseau.

        :param params: liste contenant le type de vaisseau a creer
        """
        type_vaisseau = params[0]
        if type_vaisseau == "Cargo":
            v = Cargo(self, self.nom, self.etoilemere.x + 10,
                      self.etoilemere.y)
        else:
            v = Vaisseau(self, self.nom, self.etoilemere.x + 10,
                         self.etoilemere.y)
        self.flotte[type_vaisseau][v.id] = v

        if self.nom == self.parent.parent.mon_nom:
            self.parent.parent.lister_objet(type_vaisseau, v.id)
        return v

    def ciblerflotte(self, ids: tuple) -> None:
        """Fonction de ciblage d'un vaisseau.

        :param ids: tuple contenant l'id du vaisseau qui cible et l'id de la
        cible et le type de cible (Etoile ou Porte_de_ver)
        """
        idori, iddesti, type_cible = ids
        ori = None
        for i in self.flotte.keys():
            if idori in self.flotte[i]:
                ori = self.flotte[i][idori]

        if ori:
            if type_cible == "Etoile":
                for j in self.parent.etoiles:
                    if j.id == iddesti:
                        ori.acquerir_cible(j, type_cible)
                        return
            elif type_cible == "Porte_de_ver":
                cible = None
                for j in self.parent.trou_de_vers:
                    if j.porte_a.id == iddesti:
                        cible = j.porte_a
                    elif j.porte_b.id == iddesti:
                        cible = j.porte_b
                    if cible:
                        ori.acquerir_cible(cible, type_cible)
                        return

    def jouer_prochain_coup(self):
        """Fonction de jeu du joueur pour un tour.
        """
        self.avancer_flotte()

    def avancer_flotte(self, chercher_nouveau=0):
        """Fonction d'avancement de la flotte du joueur.

        :param chercher_nouveau: si 1, le joueur cherche une nouvelle cible
        todo: ??? int only ???
        """
        for i in self.flotte:
            for j in self.flotte[i]:
                j = self.flotte[i][j]
                rep = j.jouer_prochain_coup(chercher_nouveau)
                if rep:
                    if rep[0] == "Etoile":
                        # NOTE  est-ce qu'on doit retirer l'etoile de la liste du modele
                        #       quand on l'attribue aux etoilescontrolees
                        #       et que ce passe-t-il si l'etoile a un proprietaire ???
                        self.etoilescontrolees.append(rep[1])
                        self.parent.parent.afficher_etoile(self.nom, rep[1])
                    elif rep[0] == "Porte_de_ver":
                        pass


# IA- nouvelle classe de joueur
class IA(Joueur):
    """Classe de l'IA.

    L'IA est le personnage non-joueur qui joue le jeu.
    """
    def __init__(self, parent: Modele, nom: str,
                 etoilemere: Etoile, couleur: str) -> None:
        """Initialise l'IA.

        :param parent: le jeu auquel l'IA appartient
        :param nom: le nom de l'IA
        :param etoilemere: l'etoile mere de l'IA
        :param couleur: la couleur de l'IA
        """
        Joueur.__init__(self, parent, nom, etoilemere, couleur)
        self.cooldownmax: int = 1000
        """Cooldown max de l'IA avant son prochain vaisseau."""
        self.cooldown: int = 20
        """Cooldown en cours de l'IA avant son prochain vaisseau."""

    def jouer_prochain_coup(self) -> None:
        """Fonction de jeu de l'IA pour un tour.

        Á chaque coup, L'IA avance ses flottes.
        Si le cooldown est à 0, l'IA crée un vaisseau et lui donne une cible.
        Sinon, le cooldown est décrémenté.
        """
        # for i in self.flotte:
        #     for j in self.flotte[i]:
        #         j=self.flotte[i][j]
        #         rep=j.jouer_prochain_coup(1)
        #         if rep:
        #             self.etoilescontrolees.append(rep[1])
        self.avancer_flotte(1)

        if self.cooldown == 0:
            v = self.creervaisseau(["Vaisseau"])
            cible = random.choice(self.parent.etoiles)
            v.acquerir_cible(cible, "Etoile")
            self.cooldown = random.randrange(
                self.cooldownmax) + self.cooldownmax
        else:
            self.cooldown -= 1


# début de la classe population, Concept pour incrémentation de la population
class population():
    def __init__(self):
        self.nb_humains = 10000
        self.is_under_siege = False
        self.nourritureTotal = 0
    def increment_pop(self, nbPlanetes: dict, nbBatiments: dict):
        for value in  nbPlanetes.values():
            if nbPlanetes.values() == "Bouffe":
                self.nourritureTotal += 100





class Modele():
    """Classe du modèle.

    Le modèle contient les données du jeu.
    """
    def __init__(self, parent, joueurs):
        """Initialise le modèle.

        :param parent: le jeu auquel le modèle appartient
        :param joueurs: les joueurs du jeu
        """
        self.parent = parent  # todo: type
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
            x1 = random.randrange(self.largeur - (2 * bordure)) + bordure
            y1 = random.randrange(self.hauteur - (2 * bordure)) + bordure
            x2 = random.randrange(self.largeur - (2 * bordure)) + bordure
            y2 = random.randrange(self.hauteur - (2 * bordure)) + bordure
            self.trou_de_vers.append(Trou_de_vers(x1, y1, x2, y2))

    def creeretoiles(self, joueurs: dict, ias: int = 0):
        """Crée des étoiles, d'une certaine couleur dependant du joueur.

        Créé des étoiles aléatoirement dans le modèle dependant du nombre
        d'étoiles du modèle. Les étoiles sont ajoutées à la liste des étoiles
        du modèle et retirée du compteur des étoiles à créer.

        :param joueurs: les joueurs du jeu
        :param ias: le nombre d'IA à créer
        """
        bordure = 10
        for i in range(self.nb_etoiles):
            x = random.randrange(self.largeur - (2 * bordure)) + bordure
            y = random.randrange(self.hauteur - (2 * bordure)) + bordure
            self.etoiles.append(Etoile(self, x, y))
        np = len(joueurs) + ias
        etoile_occupee = []
        while np:
            p = random.choice(self.etoiles)
            if p not in etoile_occupee:
                etoile_occupee.append(p)
                self.etoiles.remove(p)
                np -= 1

        couleurs = ["red", "blue", "lightgreen", "yellow",
                    "lightblue", "pink", "gold", "purple"]
        for i in joueurs:
            etoile = etoile_occupee.pop(0)
            self.joueurs[i] = Joueur(self, i, etoile, couleurs.pop(0))
            x = etoile.x
            y = etoile.y
            dist = 500
            for e in range(5):
                x1 = random.randrange(x - dist, x + dist)
                y1 = random.randrange(y - dist, y + dist)
                self.etoiles.append(Etoile(self, x1, y1))

        # IA- creation des ias
        couleursia = ["orange", "green", "cyan",
                      "SeaGreen1", "turquoise1", "firebrick1"]
        for i in range(ias):
            self.joueurs["IA_" + str(i)] = IA(self, "IA_" + str(i),
                                              etoile_occupee.pop(0),
                                              couleursia.pop(0))

    ##############################################################################
    def jouer_prochain_coup(self, cadre):
        """Joue le prochain coup pour chaque objet.

        Joue le prochain coup pour chaque objet du modèle. Ils y vont dans cette ordre
        : joueur, trou de vers.

        :param cadre: le cadre à jouer
        """
        #  NE PAS TOUCHER LES LIGNES SUIVANTES  ################
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

    def creer_bibittes_spatiales(self, nb_biittes: int=0):
        """Crée des biittes spatiales. Non utilisé pour le moment.
        """
        pass

    #############################################################################
    # ATTENTION : NE PAS TOUCHER
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
                action = ast.literal_eval(i[1])

                if cadrecle not in self.actions_a_faire.keys():
                    self.actions_a_faire[cadrecle] = action
                else:
                    self.actions_a_faire[cadrecle].append(action)
    # NE PAS TOUCHER - FIN
##############################################################################
