from __future__ import annotations
import json
import urllib
import urllib.error
import urllib.parse
import urllib.request
from random import seed

from Orion_client.helper import call_wrapper, LogHelper
from Orion_client.view.view import GameView, LobbyView
from Orion_client.model.model import Model

# cprofile
from cProfile import Profile
from pstats import Stats

from typing import Callable


class Controller:
    """Controller de l'application, incluant la connection au serveur"""
    server_controller: ServerController
    model: Model

    def __init__(self):
        from helper import get_random_username
        """Initialisation du controller"""
        self.frame = 1
        """La frame actuelle du jeu"""

        self.username: str = get_random_username()
        """Le nom de l'utilisateur"""

        self.urlserveur: str = "http://127.0.0.1:8000"
        # Todo get from modele maybe ?
        """L'URL du serveur"""

        self.user_controller: LobbyController | GameController = \
            LobbyController(self.username, self.urlserveur, self.start_game)
        """Le sous-controller utilisateur courant de l'application"""

    def start(self) -> None:
        """Démarre l'application"""
        self.user_controller.start()

    def start_game(self, joueurs: list[tuple[str, str]]) -> None:
        """Debute le jeu avec les joueurs donnés en paramètre,
        tout en initialisant le modèle et le sous controller serveur
        :param joueurs: la liste des joueurs"""
        seed(12471)

        listejoueurs = []
        for i in joueurs:
            listejoueurs.append(i[0])

        self.model = Model(listejoueurs)

        self.user_controller = GameController(self.model, self.username)
        self.start()

        self.server_controller = ServerController(self.username,
                                                  self.urlserveur, self.model,
                                                  self.pause_game,
                                                  self.unpause_game)
        self.tick()

    def tick(self) -> None:
        """Loop de l'application"""
        self.server_controller.update_actions(self.frame,
                                              self.user_controller.
                                              player_actions,
                                              self.empty_player_actions)

        self.user_controller.tick(self.frame)

        if not self.user_controller.pause:
            self.frame += 1
        self.user_controller.view.after(33, self.tick)

    def empty_player_actions(self) -> None:
        """Vide les actions du joueur"""
        self.user_controller.player_actions = []

    def pause_game(self) -> None:
        """Pause the game"""
        self.user_controller.pause = True

    def unpause_game(self) -> None:
        """Unpause the game"""
        self.user_controller.pause = False


class GameController:
    """Controller de la partie"""

    def __init__(self, model: Model, username: str):
        """Initialisation du controller

        :param model: le modèle de la partie
        """
        self.log = LogHelper()
        self.username: str = username
        self.model = model
        """Le modèle de la partie"""
        self.view = GameView()
        """La vue de la partie"""
        self.player_actions: list[list[str]] = []
        self.pause: bool = False
        """Si le jeu est en pause"""

    def start(self) -> None:
        """Démarre le controller"""
        # Get the ID of the player with self.username

        user_id = self.model.get_id_by_username(self.username)
        self.view.initialize(self.model, self.username, user_id)
        self.bind_game_requests()

    def tick(self, frame) -> None:
        """Fait jouer le prochain coup du modèle"""
        if not self.pause:
            self.model.jouer_prochain_coup(frame)
            self.view.refresh(self.model)

        self.get_all_view_logs()


    def bind_game_requests(self) -> None:
        """Lie les boutons de la vue à leur fonction"""
        self.view.bind_game_requests()

    def get_all_view_logs(self):
        """Retourne la liste des logs de la vue"""
        for i in self.view.get_all_view_logs():
            self.log.add_log(i)
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

    def update_actions(self, frame: int, actions: list[str],
                       empty_player_actions: Callable):
        """Met à jour les actions du modèle
        :param frame: la frame actuelle
        :param actions: les actions à envoyer au serveur
        :param empty_player_actions: la fonction à appeler pour vider les
        actions du joueur
        :return: les actions à faire
        """
        if frame % self.frame_module == 0:
            if actions:
                actions_temp = actions
            else:
                actions_temp = None
            empty_player_actions()
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
                    self.model.ajouter_actions_a_faire(temp, frame)
            except urllib.error.URLError as e:
                print("ERREUR ", frame, e)
                self.pause_game()


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

    def on_first_connection(self):
        """Fonction à appeler lors de la première connexion"""
        temp = self.get_server_state()

        if temp[0][0]:
            string = temp[0][0]
            if string == "dispo":
                string = "Disponible"
                self.view.enable_connect_button()
                self.view.enable_restart_button()

            elif string == "attente":
                self.view.enable_restart_button()
                self.view.enable_connect_button()
                string = "En attente de joueur"
            else:
                string = "Serveur occupé"
                self.view.enable_restart_button()

            self.view.change_game_state(string)
            self.view.disable_join_server_button()

    def connect_to_server(self):
        """Se connecte au serveur"""
        temp = call_server(self.urlserveur + "/tester_jeu",
                           {"username": self.username})
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
        return call_server(self.urlserveur + "/tester_jeu",
                           {"username": self.username})

    def restart_server(self):
        """Redémarre le serveur"""
        temp = call_server(self.urlserveur + "/reset_jeu", 0)
        if temp:
            self.view.change_game_state(temp[0][0])
        self.view.enable_connect_button()

    def start_game_server(self):
        """Démarre la partie"""
        temp = call_server(self.urlserveur + "/creer_partie",
                           {"nom": self.username})
        if temp:
            self.view.change_game_state("Serveur rejoint")
            self.update_lobby()
        self.view.disable_restart_connect_button()
        self.view.enable_start_game_button()

    def add_player_to_game(self):
        """Ajoute un joueur à la partie"""
        temp = call_server(self.urlserveur + "/inscrire_joueur",
                           {"nom": self.username})
        if temp:
            self.view.change_game_state(temp[0][0])
            self.update_lobby()

        self.view.disable_restart_connect_button()

    def update_lobby(self):
        """Met à jour le lobby"""
        temp = call_server(self.urlserveur + "/boucler_sur_lobby",
                           {"nom": self.username})
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

        call_server(self.urlserveur + "/lancer_partie",
                    {"nom": self.username})
        self.start_game(self.joueurs)

    def start(self):
        """Démarre le controller de lobby"""
        self.view.initialize()
        self.view.show()
        self.view.bind_server_buttons(self.on_first_connection,
                                      self.restart_server,
                                      self.connect_to_server,
                                      self.start_game_signal,
                                      self.update_username,
                                      self.update_url)

    def update_username(self, event):
        """Met à jour le nom d'utilisateur"""
        self.username = event.widget.get()

    def update_url(self, event):
        """Met à jour l'URL du serveur"""
        self.urlserveur = event.widget.get()


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
