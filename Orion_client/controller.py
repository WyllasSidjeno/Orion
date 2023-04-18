from __future__ import annotations
import json
import time
import urllib
import urllib.error
import urllib.parse
import urllib.request
from random import seed

from Orion_client.helpers.helper import StringTypes
from Orion_client.helpers.CommandQueues import ControllerQueue, \
    ModelQueue, JoueurQueue
from Orion_client.interface import IController
from Orion_client.view.view import GameView, LobbyView
from Orion_client.model.modele import Modele

# cprofile
from cProfile import Profile
from pstats import Stats

from typing import Callable


class Controller(IController):
    """Controller de l'application, incluant la connection au serveur"""
    server_controller: ServerController
    model: Modele
    view_controller_queue: ControllerQueue
    controller_server_model: ModelQueue
    controller_server_joueur: JoueurQueue
    view: GameView
    id: str
    previous_selection: list[str] | None

    def __init__(self):
        from Orion_client.helpers.helper import get_random_username
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

        self.view_controller_queue = ControllerQueue()
        self.model = Modele(listejoueurs, self.username)

        self.id = self.model.joueurs[self.username].id

        self.lobby_controller.view.destroy()
        self.lobby_controller = None

        self.view = GameView(self.view_controller_queue, self.username)

        self.server_controller = ServerController(self.username,
                                                  self.urlserveur,
                                                  self.pause_game,
                                                  self.unpause_game)

        self.controller_server_model = ModelQueue()
        self.controller_server_joueur = JoueurQueue()

        self.view.update()

        self.view.canvas.move_to_with_model_coords(
            self.model.joueurs[self.username].etoile_mere.x
            , self.model.joueurs[self.username].etoile_mere.y)

        self.tick()

    def tick(self) -> None:
        """Loop de l'application"""
        start_time = time.perf_counter()

        self.execute_commands(self.view_controller_queue)

        self.server_controller.update_actions(self.frame,
                                              self.controller_server_model,
                                              self.controller_server_joueur,
                                              self.model)
        if not self.pause:
            self.model.tick(self.frame)
            self.view.refresh(self.model)
            self.frame += 1

        elapsed_time = time.perf_counter() - start_time
        self.view.after(int(1000 / 15 - elapsed_time * 1000), self.tick)

    def handle_right_click(self, pos, new_tags_list):
        """Gère les interactions de la vue du jeu lors d'un clic droit sur
        le canvas."""
        if self.previous_selection:
            if self.model.is_type(self.previous_selection, "reconnaissance"):
                if self.model.is_type(new_tags_list,
                                      StringTypes.ETOILE.value) \
                        and not self.model.is_owner(new_tags_list):
                    ship_info = {"id": self.previous_selection[1],
                                 "type": self.previous_selection[3]
                                 }
                    target_info = {"id": new_tags_list[1],
                                   "type": new_tags_list[0],
                                   "pos": pos}
                    self.controller_server_model.target_change_request(
                        ship_info, target_info)

            elif self.model.is_type(self.previous_selection, "militaire"):
                if self.model.is_type(
                        new_tags_list, [StringTypes.ETOILE_OCCUPEE.value,
                                        StringTypes.VAISSEAU.value]) \
                        and not self.model.is_owner(new_tags_list):
                    ship_info = {"id": self.previous_selection[1],
                                 "type": self.previous_selection[3]
                                 }
                    target_info = {"id": new_tags_list[1],
                                   "type": new_tags_list[0],
                                   "owner": new_tags_list[2],
                                   "pos": pos
                                   }

                    self.controller_server_model.target_change_request(
                        ship_info, target_info)

            self.previous_selection = None

    def handle_left_click(self, pos, new_tags_list):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        le canvas."""
        self.look_for_etoile_window_interactions(new_tags_list)

        self.look_for_ship_interactions(new_tags_list, pos)

    def look_for_etoile_window_interactions(self, tags_list: list[str]):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        une etoile dans le canvas."""
        if self.model.is_owner_and_is_type(tags_list,
                                           StringTypes.ETOILE_OCCUPEE.value):
            self.view.canvas.etoile_window.show(tags_list[1])

    def look_for_ship_interactions(self, tags_list: list[str],
                                   pos: tuple[int, int]):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        un vaisseau dans le canvas sur la selection actuelle et la selection
        précédente."""
        if self.model.is_owner_and_is_type(tags_list,
                                           StringTypes.VAISSEAU.value):
            if self.previous_selection is None:
                self.previous_selection = tags_list
        elif self.previous_selection is not None:

            ship_info = {
                "id": self.previous_selection[1],
                "type": self.previous_selection[3]
            }

            target_info = {"pos": pos}

            self.controller_server_model.target_change_request(
                ship_info, target_info)

            self.previous_selection = None

    def handle_ship_construct_request(self, *args):
        """Gère la demande de construction d'un vaisseau."""
        self.controller_server_joueur.construct_ship_request(*args)

    def handle_building_construct_request(self, planete, type_building, i):
        """Gère la demande de construction d'un vaisseau."""
        self.controller_server_joueur.construct_building_request(
            planete, type_building, i
        )

    def handle_message(self, message):
        """"Gère un message pris de la vue du jeu et le transmet au serveur."""
        send = self.username + " : " + message
        self.controller_server_model.receive_message(send)

    def cancel_previous_selection(self):
        """Annule la selection précédente."""
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
        self.frame_module = 2  # Retirer du update action pour testing
        """Le nombre de frames entre chaque appel au serveur"""

        self.pause_game = pause_game
        """La fonction à appeler pour mettre le jeu en pause"""
        self.unpause_game = unpause_game
        """La fonction à appeler pour mettre le jeu en cours"""

    def update_actions(self, frame: int, actionsmodel, actionplayer, model):
        """Met à jour les actions du modèle
        :param frame: la frame actuelle
        :param actionsmodel: les actions du modèle
        :param actionplayer: les actions du joueur
        :param model: le modèle de la partie
        actions du joueur
        :return: les actions à faire
        """
        act_player = actionplayer.get_all()
        act_model = actionsmodel.get_all()

        actions_temp = []
        for action in act_model:
            new_action = ("model", *action)
            actions_temp.append(new_action)
        for action in act_player:
            new_action = (self.username, *action)
            actions_temp.append(new_action)

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

    def start_game_signal(self):
        """Reçoit le signal de démarrage de la partie et
        annule l'appel à la fonction update_lobby avant de
        démarrer la partie"""
        self.view.after_cancel(self.event_id)
        self.view.destroy()

        call_server(self.urlserveur + "/lancer_partie",
                    {"nom": self.username})
        self.start_game(self.joueurs)

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
