from __future__ import annotations
import json
import time
import urllib
import urllib.error
import urllib.parse
import urllib.request
from random import seed

from Orion_client.helper import CommandQueue
from Orion_client.view.view import GameView, LobbyView
from Orion_client.model.modele import Modele

# cprofile
from cProfile import Profile
from pstats import Stats

from typing import Callable


class Controller:
    """Controller de l'application, incluant la connection au serveur"""
    server_controller: ServerController
    model: Modele
    command_queue: CommandQueue
    view: GameView
    id: str
    previous_selection: list[str] | None

    def __init__(self):
        from helper import get_random_username
        """Initialisation du controller"""
        self.frame = 0
        """La frame actuelle du jeu"""
        self.pause: bool = False

        self.username: str = get_random_username()
        """Le nom de l'utilisateur"""

        self.urlserveur: str = "http://127.0.0.1:8000"
        # Todo get from modele maybe ?
        """L'URL du serveur"""

        self.lobby_controller = \
            LobbyController(self.username, self.urlserveur, self.start_game)
        """Le sous-controller utilisateur courant de l'application"""

    def start_game(self, joueurs: list[tuple[str, str]]) -> None:
        """Debute le jeu avec les joueurs donnés en paramètre,
        tout en initialisant le modèle et le sous controller serveur
        :param joueurs: la liste des joueurs"""
        seed(12471)

        self.previous_selection = None

        listejoueurs = []
        for i in joueurs:
            listejoueurs.append(i[0])

        self.command_queue = CommandQueue(listejoueurs, self.username)
        self.model = Modele(listejoueurs, self.command_queue)

        self.id = self.model.joueurs[self.username].id

        self.lobby_controller.view.destroy()
        self.lobby_controller = None

        self.view = GameView(self.command_queue)
        self.view.initialize(self.model, self.username,
                             self.model.joueurs[self.username].id)

        self.server_controller = ServerController(self.username,
                                                  self.urlserveur,
                                                  self.pause_game,
                                                  self.unpause_game)
        self.tick()

    def tick(self) -> None:
        """Loop de l'application"""
        start_time = time.perf_counter()
        controller_commands = self.command_queue.get_all_for_controller()
        for command in controller_commands:
            if command[1] == "handle_right_click":
                self.handle_right_click(command[2][0], command[2][1])
            elif command[1] == "handle_left_click":
                self.handle_left_click(command[2][0], command[2][1])

        self.server_controller.update_actions(self.frame,
                                              self.command_queue,
                                              self.model)
        if not self.pause:
            self.model.tick(self.frame)
            self.view.refresh(self.model)
            self.frame += 1

        elapsed_time = time.perf_counter() - start_time
        self.view.after(int(1000 / 15 - elapsed_time * 1000), self.tick)
        # This represents 15 fps because : 1000ms / 15 = 66.66666666666667 ms
        # per frame which is the time we want to wait between each frame
        # and mathematically : 1000ms / 66.66666666666667 = 15 fps

    def handle_right_click(self, pos, new_tags_list):
        if self.previous_selection:
            if self.is_type(self.previous_selection, "reconnaissance"):
                if self.is_type(new_tags_list, "etoile") \
                        and not self.is_owner(new_tags_list):
                    print("recon to star request")
            elif self.is_type(self.previous_selection, "militaire"):
                if self.is_type(new_tags_list, "etoile_occupee") \
                        and not self.is_owner(new_tags_list):
                    self.command_queue.add(self.username,
                                           "ship_target_change_request",
                                           self.previous_selection[1],
                                           self.previous_selection[3],
                                           pos, new_tags_list[1],
                                           new_tags_list[0], new_tags_list[2])
            self.previous_selection = None

    def handle_left_click(self, pos, new_tags_list):
        self.look_for_etoile_window_interactions(new_tags_list)

        self.look_for_ship_interactions(new_tags_list, pos)

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
        return self.username in tags_list or self.username in tags_list

    def cancel_previous_selection(self):
        """Annule la selection précédente."""
        self.previous_selection = None

    def look_for_etoile_window_interactions(self, tags_list: list[str]):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        une etoile dans le canvas."""
        print(tags_list)
        if self.is_owner_and_is_type(tags_list, "etoile_occupee"):
            self.view.canvas.planet_window.show(tags_list[1])

    def look_for_ship_interactions(self, tags_list: list[str],
                                   pos: tuple[int, int]):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        un vaisseau dans le canvas sur la selection actuelle et la selection
        précédente."""
        if self.is_owner_and_is_type(tags_list, "vaisseau"):
            if self.previous_selection is None:
                self.previous_selection = tags_list
        elif self.previous_selection is not None:
            self.command_queue.add(self.username,
                                   "ship_target_change_request",
                                   self.previous_selection[1],
                                   self.previous_selection[3], pos)

            self.previous_selection = None

    def pause_game(self) -> None:
        """Pause the game"""
        self.pause = True

    def unpause_game(self) -> None:
        """Unpause the game"""
        self.pause = False


class ServerController:
    """Controller du serveur"""
    def __init__(self, username: str, url_serveur: str,
                 pause_game: Callable, unpause_game: Callable):
        """Initialisation du controller

        :param username: le nom de l'utilisateur
        :param url_serveur: l'URL du serveur
        :param pause_game: la fonction à appeler pour mettre le jeu en pause
        :param unpause_game: la fonction à appeler pour mettre le jeu en pause
        """
        self.username: str = username
        """Le nom de l'utilisateur"""
        self.url_serveur: str = url_serveur
        """L'URL du serveur"""
        self.frame_module = 2
        """Le nombre de frames entre chaque appel au serveur"""

        self.pause_game = pause_game
        """La fonction à appeler pour mettre le jeu en pause"""
        self.unpause_game = unpause_game
        """La fonction à appeler pour mettre le jeu en cours"""

    def update_actions(self, frame: int, actions, model):
        """Met à jour les actions du modèle
        :param frame: la frame actuelle
        :param actions: les actions à envoyer au serveur
        :param model: le modèle de la partie
        actions du joueur
        :return: les actions à faire
        """
        if frame % self.frame_module == 0:
            if actions:
                actions_temp = actions.get_all()
            else:
                actions_temp = None
            actions.clear()
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
                    model.ajouter_actions(temp, frame)
            except urllib.error.URLError as e:
                print("ERREUR ", frame, e)
                self.pause_game()


class LobbyController:
    """Controller du lobby"""
    model: Modele
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

        self.view.initialize()

        self.view.show()

        self.view.bind_server_buttons(self.on_first_connection,
                                      self.restart_server,
                                      self.connect_to_server,
                                      self.start_game_signal,
                                      self.update_username,
                                      self.update_url)

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
                           {"nom": self.username})
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
                           {"nom": self.username})

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
        controller.lobby_controller.view.master.title("Orion")
        controller.lobby_controller.view.mainloop()

        Stats(p).sort_stats('cumtime').print_stats(20)
