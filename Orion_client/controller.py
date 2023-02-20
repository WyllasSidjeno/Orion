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
    """Le modèle de l'application"""

    def __init__(self):
        """Initialisation du controller"""
        self.frame = 1
        """La frame actuelle du jeu"""

        self.username: str = "p1"  # todo: Check JM code
        """Le nom de l'utilisateur"""

        self.server_actions: list[str] = []  # todo : Make sure
        """Liste des actions reçues du serveur"""
        self.player_actions: list[str] = []  # todo Make sure
        """Liste des actions à envoyées au serveur, faite par le joueur
        de ce client."""

        self.urlserveur: str = "http://127.0.0.1:8000"  # Todo get from modele maybe ?
        """L'URL du serveur"""

        self.view: LobbyView | GameView = LobbyView(
            self.urlserveur, self.username)
        """La vue courante de l'application"""

        self.user_controller: LobbyController | GameController = \
            LobbyController(self.username, self.urlserveur,
                            self.view, self.start_game)
        """Le sous-controller utilisateur courant de l'application"""

        self.server_controller: ServerController
        """Le sous-controller serveur de l'application"""

    def change_view(self) -> None:
        """Change la vue de l'application vers la vue de jeu
        du modèle donné en paramètre
        :param mod: le modèle de jeu"""
        self.view.destroy()
        self.view = GameView()

    def start_game(self, joueurs: list[tuple[str, str]]) -> None:
        """Debute le jeu avec les joueurs donnés en paramètre,
        tout en initialisant le modèle et le sous controller serveur
        :param joueurs: la liste des joueurs"""
        seed(12471)
        print(type(joueurs))
        print(joueurs)

        listejoueurs = []
        for i in joueurs:
            listejoueurs.append(i[0])

        print(type(listejoueurs))
        print(listejoueurs)

        self.model = Model(self, listejoueurs)

        self.change_view()
        self.view.initialize(self.model)


        self.user_controller = GameController(self.model, self.view)
        self.user_controller.start()
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
        self.view.after(1000 // 60, self.tick)  # -> 60 fps

        self.user_controller.tick(self.frame)
        self.frame += 1

    def update_model_actions(self, actions) -> None:
        """Met à jour les actions du modèle"""
        self.model.ajouter_actions_a_faire(actions)

    def start(self) -> None:
        """Démarre l'application"""
        self.view.initialize()
        self.view.show()

        self.user_controller.start()


class GameController:
    """Controller de la partie"""
    def __init__(self, model: Model, view: GameView):
        """Initialisation du controller

        :param model: le modèle de la partie
        :param view: la vue de la partie"""
        self.model = model
        """Le modèle de la partie"""
        self.view = view
        """La vue de la partie"""
        self.player_actions = []
        """Liste des actions à envoyer au serveur"""
        self.server_actions = []
        """Liste des actions reçues du serveur"""
        self.frame = 1
        """La frame actuelle du jeu"""
        self.pause: bool = False
        """Si le jeu est en pause"""

    def start(self) -> None:
        """Bind les boutons de la partie"""
        self.view.canvas.bind("<MouseWheel>",
                              self.view.canvas.vertical_scroll)
        self.view.canvas.bind("<Control-MouseWheel>", self.
                              view.canvas.horizontal_scroll)

        self.view.canvas.bind("<Button-1>", self.print_tags)  # DEBUG

    def print_tags(self, _) -> None:
        """Print the tags of the current object"""
        print(self.view.canvas.gettags("current"))
        # xy
        print(self.view.canvas.coords("current"))

    def update_model_actions(self, actions: list[str]) -> None:
        """Met à jour les actions du modèle"""
        self.model.ajouter_actions_a_faire(actions)

    def tick(self, frame) -> None:
        """Fait jouer le prochain coup du modèle"""
        if not self.pause:
            self.model.jouer_prochain_coup(frame)
            self.view.refresh(self.model)


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
                 view: LobbyView, start_game: Callable):
        self.username: str = username
        """Le nom de l'utilisateur"""
        self.urlserveur: str = urlserveur
        """L'URL du serveur"""
        self.view = view
        """La vue du lobby"""

        self.start_game = start_game
        """La fonction à appeler pour démarrer la partie"""

    def connect_to_server(self, _):
        """Se connecte au serveur"""
        # Todo : Could be renamed to : connect_to_lobby or get_lobby_state
        print("Connecting to server...")
        url = self.urlserveur + "/tester_jeu"
        params = {"username": self.username}
        temp = call_server(url, params)
        if temp[0][0]:
            string = temp[0][0]
            self.view.change_game_state(string)
            if string == "dispo":
                self.start_game_server()
            elif string == "attente":
                pass

    def restart_server(self, _):
        """Redémarre le serveur"""
        print("Restarting server...")
        url = self.urlserveur + "/reset_jeu"
        temp = call_server(url, None)
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
            self.view.after(1000, self.update_lobby)

    def start(self):
        """Démarre le controller de lobby"""
        self.view.show()
        self.view.connect_button.bind("<Button-1>", self.connect_to_server)
        self.view.restart_button.bind("<Button-1>", self.restart_server)

    def update_lobby(self):
        """Met à jour le lobby"""
        url = self.urlserveur + "/boucler_sur_lobby"
        params = {"nom": self.username}
        temp = call_server(url, params)
        if 'courante' in temp:
            self.start_game_signal(temp)
        else:
            self.joueurs = temp
            self.view.update_player_list(self.joueurs[0])
            self.event_id = self.view.after(1000, self.update_lobby)
            self.view.start_button.bind("<Button-1>",
                                        self.start_game_signal)

    def start_game_signal(self, _):
        """Reçoit le signal de démarrage de la partie et
        annule l'appel à la fonction update_lobby avant de
        démarrer la partie"""
        self.view.after_cancel(self.event_id)

        self.start_game(self.joueurs)


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
        controller.view.master.title("Orion")
        controller.view.mainloop()

        Stats(p).sort_stats('cumtime').print_stats(20)
