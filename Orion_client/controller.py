from __future__ import annotations
import json
import urllib
import urllib.error
import urllib.parse
import urllib.request
from random import seed

from Orion_client.view.view import GameView, LobbyView
from Orion_client.model.model import Model

# cprofile
from cProfile import Profile
from pstats import Stats

from typing import Callable


class Controller:
    """Controller de l'application, incluant la connection au serveur"""
    model: Model
    server_controller: ServerController

    def __init__(self):
        from helper import get_random_username
        """Initialisation du controller"""
        self.frame = 1
        """La frame actuelle du jeu"""

        self.username: str = get_random_username()
        """Le nom de l'utilisateur"""

        self.server_actions: list[str] = []
        """Liste des actions reçues du serveur"""
        self.player_actions: list[str] = []
        """Liste des actions à envoyées au serveur, faite par le joueur
        de ce client."""

        self.urlserveur: str = "http://127.0.0.1:8000"
        # Todo get from modele maybe ?
        """L'URL du serveur"""

        self.user_controller: LobbyController | GameController = \
            LobbyController(self.username, self.urlserveur, self.start_game)
        """Le sous-controller utilisateur courant de l'application"""

    def start_game(self, joueurs: list[tuple[str, str]]) -> None:
        """Debute le jeu avec les joueurs donnés en paramètre,
        tout en initialisant le modèle et le sous controller serveur
        :param joueurs: la liste des joueurs"""
        seed(12471)

        listejoueurs = []
        for i in joueurs:
            listejoueurs.append(i[0])

        self.model = Model(self, listejoueurs)

        self.user_controller = GameController(self.model)
        self.start()

        self.server_controller = ServerController(self.username,
                                                  self.urlserveur, self.model,
                                                  self.pause_game,
                                                  self.unpause_game)
        self.tick()

    def pause_game(self) -> None:
        """Pause the game"""
        self.user_controller.pause = True

    def unpause_game(self) -> None:
        """Unpause the game"""
        self.user_controller.pause = False

    def tick(self) -> None:
        """Loop de l'application"""
        temp = self.server_controller.update_actions(self.frame,
                                                     self.player_actions)

        if temp is not None:
            self.update_model_actions(temp)
        self.user_controller.view.after(1000 // 60, self.tick)

        self.user_controller.tick(self.frame)
        if not self.user_controller.pause:
            self.frame += 1

    def update_model_actions(self, actions) -> None:
        """Met à jour les actions du modèle"""
        self.model.ajouter_actions_a_faire(actions)

    def start(self) -> None:
        """Démarre l'application"""
        self.user_controller.start()


class GameController:
    """Controller de la partie"""

    def __init__(self, model: Model):
        """Initialisation du controller

        :param model: le modèle de la partie
        """
        self.model = model
        """Le modèle de la partie"""
        self.view = GameView()
        """La vue de la partie"""
        self.player_actions = []
        """Liste des actions à envoyer au serveur"""
        self.server_actions = []
        """Liste des actions reçues du serveur"""
        self.frame = 1
        """La frame actuelle du jeu"""
        self.pause: bool = False
        """Si le jeu est en pause"""

    def update_model_actions(self, actions: list[str]) -> None:
        """Met à jour les actions du modèle"""
        self.model.ajouter_actions_a_faire(actions)

    def tick(self, frame) -> None:
        """Fait jouer le prochain coup du modèle"""
        if not self.pause:
            self.model.jouer_prochain_coup(frame)
            self.view.refresh(self.model)

    def start(self) -> None:
        """Démarre le controller"""
        self.view.initialize(self.model)


class ServerController:
    """Controller du serveur"""

    def __init__(self, username: str, url_serveur: str,
                 model: Model, pause_game: Callable, unpause_game: Callable):
        """Initialisation du controller

        :param username: le nom de l'utilisateur
        :param url_serveur: l'URL du serveur
        :param model: le modèle de la partie
        :param pause_game: la fonction à appeler pour mettre le jeu en pause
        :param unpause_game: la fonction à appeler pour mettre le jeu en pause
        """
        self.username: str = username
        """Le nom de l'utilisateur"""
        self.url_serveur: str = url_serveur
        """L'URL du serveur"""
        self.frame_module = 2
        """Le nombre de frames entre chaque appel au serveur"""

        self.model = model
        """Le modèle de la partie"""

        self.pause_game = pause_game
        """La fonction à appeler pour mettre le jeu en pause"""
        self.unpause_game = unpause_game
        """La fonction à appeler pour mettre le jeu en cours"""

    def update_actions(self, frame: int, actions: list[str]) -> list[str]:
        """Met à jour les actions du modèle
        :param frame: la frame actuelle
        :param actions: les actions à envoyer au serveur
        :return: les actions à faire
        """
        if frame % self.frame_module == 0:
            if actions:
                actions_temp = actions
            else:
                actions_temp = None
            actions = []
            url = self.url_serveur + "/boucler_sur_jeu"
            params = {"nom": self.username,
                      "cadrejeu": frame,
                      "actionsrequises": actions_temp}
            try:
                temp = call_server(url, params)
                if "ATTENTION" in temp:
                    print("ATTEND QUELQU'UN")
                    self.pause_game()
                else:
                    self.unpause_game()
                    self.model.ajouter_actions_a_faire(temp)
            except urllib.error.URLError as e:
                print("ERREUR ", frame, e)
                self.pause_game()
        return actions


class LobbyController:
    """Controller du lobby"""
    model: Model
    """Le modèle du lobby"""
    joueurs: list[list[str]]
    """La liste des joueurs"""
    event_id: str
    """L'id du prochain appel à la fonction connect_to_server"""

    def __init__(self, username: str, urlserveur: str,
                 start_game: Callable):
        self.username: str = username
        """Le nom de l'utilisateur"""
        self.urlserveur: str = urlserveur
        """L'URL du serveur"""

        self.start_game = start_game
        """La fonction à appeler pour démarrer la partie"""

        self.view = LobbyView(
            self.urlserveur, self.username)
        """La vue du lobby"""

    def connect_to_server(self):
        """Se connecte au serveur"""
        print("Connecting to server...")
        url = self.urlserveur + "/tester_jeu"
        params = {"username": self.username}
        temp = call_server(url, params)

        if temp[0][0]:
            string = temp[0][0]
            if string == "dispo":
                string = "Partie Créée"
                self.start_game_server()
            elif string == "attente":
                string = "En attente de joueur"
                self.add_player_to_game()
            self.view.change_game_state(string)
        self.view.disable_restart_connect_button()

    def get_server_state(self):
        print("Connecting to server...")
        url = self.urlserveur + "/tester_jeu"
        params = {"username": self.username}
        temp = call_server(url, params)
        if temp[0][0]:
            string = temp[0][0]
            if string == "dispo":
                string = "Disponible"
            elif string == "attente":
                string = "En attente de joueur"
            else:
                string = "Serveur occupé"

            self.update_lobby()
            self.view.change_game_state(string)
            self.view.disable_join_server_button()

    def add_player_to_game(self):
        """Ajoute un joueur à la partie"""
        print("Adding player to game...")
        url = self.urlserveur + "/inscrire_joueur"
        params = {"nom": self.username}
        temp = call_server(url, params)
        if temp:
            self.view.change_game_state(temp[0][0])

    def restart_server(self):
        """Redémarre le serveur"""
        print("Restarting server...")
        url = self.urlserveur + "/reset_jeu"
        temp = call_server(url, 0)
        if temp:
            self.view.change_game_state(temp[0][0])

    def start_game_server(self):
        """Démarre la partie"""
        print("Starting game server...")
        url = self.urlserveur + "/creer_partie"
        params = {"nom": self.username}
        temp = call_server(url, params)
        if temp:
            self.view.change_game_state(temp[0][0])

    def start(self):
        """Démarre le controller de lobby"""
        self.view.initialize()
        self.view.show()
        self.view.bind_server_buttons(self.get_server_state,
                                      self.restart_server,
                                      self.connect_to_server,
                                      self.start_game_signal,
                                      self.update_username,
                                      self.update_url)

    def update_lobby(self):
        """Met à jour le lobby"""
        url = self.urlserveur + "/boucler_sur_lobby"
        params = {"nom": self.username}
        temp = call_server(url, params)
        if 'courante' in temp:
            self.start_game_signal()
        else:
            self.joueurs = temp
            self.view.update_player_list(self.joueurs)
            self.event_id = self.view.after(1000, self.update_lobby)

    def start_game_signal(self):
        """Reçoit le signal de démarrage de la partie et
        annule l'appel à la fonction update_lobby avant de
        démarrer la partie"""
        self.view.after_cancel(self.event_id)
        self.view.destroy()

        self.start_game(self.joueurs)

    def update_username(self, event):
        """Met à jour le nom d'utilisateur"""
        username = event.widget.get()
        self.username = username

    def update_url(self, event):
        """Met à jour l'URL du serveur"""
        url = event.widget.get()
        self.urlserveur = url


def call_server(url, params):
    """Appelle le serveur et renvoie la réponse sous forme de dictionnaire
    :param url: l'URL du serveur
    :param params: les paramètres à envoyer au serveur
    :return: la réponse du serveur sous forme de dictionnaire
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
    return rep


if __name__ == "__main__":
    with Profile() as p:
        controller = Controller()
        controller.start()
        controller.user_controller.view.master.title("Orion")
        controller.user_controller.view.mainloop()

        Stats(p).sort_stats('cumtime').print_stats(20)
