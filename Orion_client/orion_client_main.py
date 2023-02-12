""" Controlleur du jeu Orion

    Cette classe contient les methodes pour gerer le jeu Orion.
    Elle est responsable de la communication avec le serveur et de la gestion
    des evenements de la fenetre de jeu. Elle est aussi responsable de la
    creation du modele et de la vue.
"""
# -*- coding: utf-8 -*-

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from orion_modele import *
from orion_vue import *


class Controleur():
    """Controlleur du jeu Orion

    Cette classe contient les methodes pour gerer le jeu Orion.
    Elle est responsable de la communication avec le serveur et de la gestion
    des evenements de la fenetre de jeu. Elle est aussi responsable de la
    creation du modele et de la vue.
    """

    def __init__(self):
        """Constructeur de la classe"""
        self.mon_nom: str = self.generer_nom()
        """Nom de joueur, sert d'identifiant dans le jeu - ici, 
        avec auto-generation"""
        self.joueur_createur: int = 0
        """1 quand un joueur "Créer une partie", peut Demarrer la partie"""
        self.cadrejeu: int = 0
        """compte les tours dans la boucle de jeu (bouclersurjeu)"""
        self.actionsrequises: list = []
        """les actions envoyées au serveur"""
        self.joueurs: list = []
        """liste des noms de joueurs pour le lobby"""

        # TODO: Make sure the other type is bool with jm.
        self.prochainsplash: bool | None = None
        """requis pour sortir de cette boucle et passer au lobby du jeu"""
        self.onjoue: int = 1
        """indicateur que le jeu se poursuive - sinon on attend qu'un autre joueur nous rattrape"""
        self.maindelai: int = 50
        """delai en ms de la boucle de jeu"""
        self.moduloappeler_serveur: int = 2
        """frequence des appel au serveur, evite de passer son temps a communiquer avec le serveur"""
        self.urlserveur: str = "http://127.0.0.1:8000"
        """127.0.0.1 pour tests,"http://votreidentifiant.pythonanywhere.com" pour web"""
        # self.urlserveur= "http://jmdeschamps.pythonanywhere.com"
        self.modele: None | Modele = None  # Todo: JM
        """la variable contenant la partie, après initialiserpartie()"""
        self.vue: Vue = Vue(self, self.urlserveur, self.mon_nom,
                            "Non connecté")
        """la vue pour l'affichage et les controles du jeu"""

        self.vue.root.mainloop()
        """ La loop principale du jeu, incluant les evenements souris, 
        clavier, etc."""

    ##################################################################
    # FONCTIONS RESERVEES - INTERDICTION DE MODIFIER SANS AUTORISATION
    # PREALABLE SAUF CHOIX DE RANDOM SEED LIGNE 94-95
    def connecter_serveur(self, url_serveur) -> None:
        """Connexion au serveur

        :param url_serveur: URL du serveur
        """
        self.urlserveur = url_serveur
        """le dernier avant le clic"""
        self.boucler_sur_splash()

    # a partir du splash
    def creer_partie(self, nom: str) -> None:
        """Creation d'une partie

        :param nom: Nom du joueur qui crée la partie
        """
        if self.prochainsplash:
            # si on est dans boucler_sur_splash, on doit supprimer
            # le prochain appel
            self.vue.root.after_cancel(self.prochainsplash)
            self.prochainsplash = None
        if nom:  # si c'est pas None c'est un nouveau nom
            self.mon_nom = nom
        # on avertit le serveur qu'on cree une partie
        url = self.urlserveur + "/creer_partie"
        params = {"nom": self.mon_nom}
        reptext = self.appeler_serveur(url, params)
        """Reponse du serveur"""

        self.joueur_createur = 1
        """on est le createur"""
        self.vue.root.title("je suis " + self.mon_nom)
        # on passe au lobby pour attendre les autres joueurs
        self.vue.changer_cadre("lobby")
        self.boucler_sur_lobby()

    # un joueur s'inscrit à la partie, similaire à creer_partie
    def inscrire_joueur(self, nom: str, urljeu: str) -> None:
        """Inscription d'un joueur à la partie

        :param nom: Nom du joueur
        :param urljeu: URL du jeu
        """
        # on quitte le splash et sa boucle
        if self.prochainsplash:
            self.vue.root.after_cancel(self.prochainsplash)
            self.prochainsplash = None
        if nom:
            self.mon_nom = nom
        # on s'inscrit sur le serveur
        url = self.urlserveur + "/inscrire_joueur"
        params = {"nom": self.mon_nom}
        """Parametre a envoyer au serveur"""
        reptext = self.appeler_serveur(url, params)
        """Reponse du serveur"""

        self.vue.root.title("je suis " + self.mon_nom)
        self.vue.changer_cadre("lobby")
        self.boucler_sur_lobby()

    # a partir du lobby, le createur avertit le serveur de changer l'etat pour courant
    def lancer_partie(self):
        """Lancement de la partie"""
        url = self.urlserveur + "/lancer_partie"
        params = {"nom": self.mon_nom}
        reptext = self.appeler_serveur(url, params)
        """Reponse du serveur"""

    # Apres que le createur de la partie ait lancer_partie
    # boucler_sur_lobby a reçu code ('courant') et appel cette fonction pour tous
    def initialiser_partie(self, mondict: dict) -> None:
        """Initialisation de la partie avec seed aléatoire ou non
        """
        initaleatoire = mondict[1][0][0]
        """ Le seed aléatoire pour la partie si voulue"""
        random.seed(12471)  # random FIXE pour test ou ...
        # random.seed(int(initaleatoire))   # qui prend la valeur generer par le serveur

        listejoueurs = []
        """liste des joueurs pour la partie"""
        for i in self.joueurs:
            listejoueurs.append(i[0])

        # on cree une partie pour les joueurs, qu'on conserve comme modele
        self.modele = Modele(self,
                             listejoueurs)

        # on fournit le modele et mets la vue à jour
        self.vue.initialiser_avec_modele(
            self.modele)

        # on change le cadre la fenetre pour passer dans l'interface de jeu
        self.vue.changer_cadre(
            "partie")

        # on lance la boucle de jeu
        self.boucler_sur_jeu()

    ##########   BOUCLES: SPLASH, LOBBY ET JEU    #################
    def boucler_sur_splash(self) -> None:
        """Boucle de communication intiale avec le serveur pour creer
        ou s'inscrire a la partie
        """
        url = self.urlserveur + "/tester_jeu"
        params = {"nom": self.mon_nom}
        mondict = self.appeler_serveur(url, params)
        if mondict:
            self.vue.update_splash(mondict[0])
        self.prochainsplash = self.vue.root.after(50, self.boucler_sur_splash)

    # on boucle sur le lobby en attendant le demarrage
    def boucler_sur_lobby(self) -> None:
        """Boucle de communication avec le serveur pour mettre a jour
        la liste des joueurs jusqu'a ce que la partie commence
        (par appel "courante")
        """
        url = self.urlserveur + "/boucler_sur_lobby"
        params = {"nom": self.mon_nom}
        mondict = self.appeler_serveur(url, params)
        """Dictionnaire de reponse du serveur"""

        if "courante" in mondict[
            0]:  # courante, la partie doit etre initialiser
            self.initialiser_partie(mondict)
        else: # sinon on met a jour la liste des joueurs
            self.joueurs = mondict
            self.vue.update_lobby(mondict)
            self.vue.root.after(50, self.boucler_sur_lobby)

    # BOUCLE PRINCIPALE
    def boucler_sur_jeu(self) -> None:
        """Boucle principale du jeu
        todo: Add more context here
        """
        self.cadrejeu += 1
        # increment du compteur de boucle de jeu

        # appel périodique au serveur pour récupérer les actions requises
        if self.cadrejeu % self.moduloappeler_serveur == 0:
            if self.actionsrequises:
                actions = self.actionsrequises
            else:
                actions = None
            self.actionsrequises = []
            url = self.urlserveur + "/boucler_sur_jeu"
            params = {"nom": self.mon_nom,
                      "cadrejeu": self.cadrejeu,
                      "actionsrequises": actions}
            try:  # permet de récupérer des time-out, mais aussi des commandes
                # de pause du serveur pour retard autre joueur
                mondict = self.appeler_serveur(url, params)

                if "ATTENTION" in mondict:  # verifie attente d'un joueur plus lent
                    print("ATTEND QUELQU'UN")
                    self.onjoue = 0

                else:  # sinon on ajoute l'action
                    self.modele.ajouter_actions_a_faire(mondict)

            except urllib.error.URLError as e:
                print("ERREUR ", self.cadrejeu, e)
                self.onjoue = 0

        # le reste du tour vers modele et vers vue, s'il y a lieu
        if self.onjoue:
            # envoyer les messages au modele et a la vue de faire leur job
            self.modele.jouer_prochain_coup(self.cadrejeu)
            self.vue.afficher_jeu()
        else:
            self.cadrejeu -= 1
            self.onjoue = 1

        # appel ulterieur de la meme fonction jusqu'a l'arret de la partie
        self.vue.root.after(self.maindelai,
                            self.boucler_sur_jeu)

    ##############   FONCTIONS pour serveur #################
    def reset_partie(self) -> dict:
        """methode speciale pour remettre les parametres du serveur
        a leurs valeurs par defaut"""
        leurl = self.urlserveur + "/reset_jeu"
        reptext = self.appeler_serveur(leurl, 0)
        self.vue.update_splash(reptext[0][0])
        return reptext

    def tester_etat_serveur(self) -> [str | Any]:
        """Fonction qui sert a tester l'etat du serveur

        :return: Un string representant l'etat du serveur, ainsi
         que son code de reponse."""
        leurl = self.urlserveur + "/tester_jeu"
        repdecode = self.appeler_serveur(leurl, None)[0]
        if "dispo" in repdecode:  # on peut creer une partie
            return ["dispo", repdecode]
        elif "attente" in repdecode:  # on peut s'inscrire a la partie
            return ["attente", repdecode]
        elif "courante" in repdecode:  # la partie est en cours
            return ["courante", repdecode]
        else:
            return "impossible"

    def appeler_serveur(self, url: str, params: dict[str, str]) -> dict:
        """fonction normalisee d'appel pendant le jeu

        :param url: url du serveur
        :param params: parametres a envoyer au serveur
        :type params: dict de string a string ('nom' : player_id)

        :return: Reponse du serveur
        """
        if params:
            query_string = urllib.parse.urlencode(params)
            data = query_string.encode("ascii")
        else:
            data = None
        rep = urllib.request.urlopen(url, data, timeout=None)
        reptext = rep.read()
        rep = reptext.decode('utf-8')
        rep = json.loads(rep)
        return rep  # This is a dictionnary because of the json.loads

    #  FIN DE L'INTERDICTION DE MODIFICATION
    ##########################################

    # OUTILS

    def generer_nom(self) -> str:
        """Generateur de nouveau nom, peut y avoir collision

        :return: nom du joueur
        """
        mon_nom = "PLAYER_" + str(random.randrange(100, 1000))
        return mon_nom

    def abandonner(self) -> None:
        """Fonction appelee par le bouton abandonner afin de
        quitter la partie
        """
        action = [self.mon_nom, "abandonner",
                  [self.mon_nom + ": J'ABANDONNE !"]]
        self.actionsrequises = action
        self.root.after(500, self.root.destroy)

    # VOTRE CODE

    def creer_vaisseau(self, type_vaisseau: str) -> None:
        """Fonction appelee afin de créer un vaisseau

        :param type_vaisseau: type de vaisseau a creer
        :type type_vaisseau: str
        todo : make sure str
        """
        self.actionsrequises.append(
            [self.mon_nom, "creervaisseau", [type_vaisseau]])

    def cibler_flotte(self, idorigine: str, iddestination: str,
                      type_cible: str) -> None:
        """
        todo : JM

        :param idorigine: id de l'origine
        :param iddestination: id de la destination
        :param type_cible: type de cible
        """
        self.actionsrequises.append([self.mon_nom, "ciblerflotte",
                                     [idorigine, iddestination, type_cible]])

    def afficher_etoile(self, joueur: str, cible: str) -> None:
        """Fonction appelee afin d'afficher une etoile dependant de
        son joueur
        todo : JM
        todo: confirm params type
        """
        self.vue.afficher_etoile(joueur, cible)

    def lister_objet(self, objet: str, id: str) -> None:
        """Fonction appelee afin de lister un objet dans la vue

        :param objet: objet a lister
        :param id: id de l'objet
        todo : JM
        todo: confirm params type
        """
        self.vue.lister_objet(objet, id)


if __name__ == "__main__":
    c = Controleur()
    print("End Orion_mini")
