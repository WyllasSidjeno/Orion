import json
import urllib
import urllib.error
import urllib.parse
import urllib.request
from random import seed

from Orion_client.view.view import App
from Orion_client.model.model import Model

# cprofile
from cProfile import Profile
from pstats import Stats


class Controller:
    """Controller de l'application, incluant la connection au serveur"""
    model: Model
    def __init__(self):
        """Initialisation du controller"""
        self.frame = 1
        self.username: str = "p1"
        self.server_actions: list[str] = []
        """Liste des actions reçues du serveur"""
        self.player_actions: list[str] = []
        """Liste des actions à envoyées au serveur"""
        self.urlserveur: str = "http://127.0.0.1:8000"

        self.app = App(self.urlserveur, self.username)

        self.user_controller = LobbyController(
            self.username,
            self.urlserveur,
            self.app,
            self.start_game)

        self.after_id = None

    def start_game(self, joueurs):
        """Start the game with the list of players"""
        seed(12471)
        ## Stop the update_lobby loop

        listejoueurs = []
        for i in joueurs:
            listejoueurs.append(i[0])
        self.model = Model(self, listejoueurs)
        self.app.change_view(self.model)

        self.user_controller = GameController(self.model, self.app)
        self.server_controller = ServerController(
            self.username,
            self.urlserveur,
            self.model,
            self.pause_game,
            self.unpause_game
        )

        self.loop()

    def pause_game(self):
        """Pause the game"""
        self.user_controller.pause = True
    def unpause_game(self):
        """Unpause the game"""
        self.user_controller.pause = False

    def loop(self):
        """Loop de l'application"""
        temp = self.server_controller.update_actions(self.frame,
                                                     self.player_actions)

        if temp is not None:
            self.update_model_actions(temp)
        self.app.after(1000 // 60, self.loop) # -> 60 fps


        self.user_controller.tick(self.frame)
        self.frame += 1

    def update_model_actions(self, actions):
        """Update the model actions"""
        self.model.ajouter_actions_a_faire(actions)


class GameController:
    """Controller de la partie"""
    pause: bool
    model: Model
    def __init__(self, model: Model, app: App):
        """Initialisation du controller"""
        self.model = model
        self.app = app
        self.after_id = None
        self.bind_game_buttons()
        self.player_actions = []
        self.server_actions = []
        self.frame = 1
        self.pause = False
    def bind_game_buttons(self):
        """Bind les boutons de la partie"""
        self.app.view.canvas.bind("<MouseWheel>",
                                  self.app.view.canvas.vertical_scroll)
        self.app.view.canvas.bind("<Control-MouseWheel>", self.app.
                                  view.canvas.horizontal_scroll)

        self.app.view.canvas.bind("<Button-1>", self.print_tags)  # DEBUG

    def print_tags(self, event):
        """Print the tags of the current object"""
        print(self.app.view.canvas.gettags("current"))
        # xy
        print(self.app.view.canvas.coords("current"))

    def update_model_actions(self, actions: list[str]):
        """Update the actions of the model"""
        self.model.ajouter_actions_a_faire(actions)

    def tick(self, frame):
        """Update the game"""
        if not self.pause:
            self.model.jouer_prochain_coup(frame)
            self.app.view.refresh(self.model)


class ServerController:
    def __init__(self, username, urlserveur,
                 model, pause_game, unpause_game):
        self.username: str = username
        self.urlserveur: str = urlserveur
        self.after_id = None

        self.gameFrame = 0
        self.gameFrameModulo = 2

        self.model = model

        self.pause_game = pause_game
        self.unpause_game = unpause_game

    def update_actions(self, cadre: int, actions : list[str]):
        if cadre % self.gameFrameModulo == 0:
            if actions:
                actionsT = actions
            else:
                actionsT = None
            actions = []
            url = self.urlserveur + "/boucler_sur_jeu"
            params = {"nom": self.username,
                      "cadrejeu": cadre,
                      "actionsrequises": actionsT}
            try:
                temp = call_server(url, params)
                if "ATTENTION" in temp:
                    print("ATTEND QUELQU'UN")
                    self.pause_game()
                else:
                    self.model.ajouter_actions_a_faire(temp)
            except urllib.error.URLError as e:
                print("ERREUR ", cadre, e)
                self.pause_game()
        return actions


class LobbyController:
    model: Model
    joueurs: list[list[str]]
    def __init__(self, username, urlserveur, app, start_game):
        self.username: str = username
        self.urlserveur: str = urlserveur
        self.app = app
        self.after_id = None

        self.start_game = start_game

        self.bind_server_buttons()

    def connect_to_server(self, _):
        print("Connecting to server...")
        url = self.urlserveur + "/tester_jeu"
        params = {"username": self.username}
        temp = call_server(url, params)
        if temp[0][0]:
            str = temp[0][0]
            self.app.view.change_game_state(str)
            if str == "dispo":
                self.start_game_server()
            elif str == "attente":
                pass

    def restart_server(self, _):
        print("Restarting server...")
        url = self.urlserveur + "/reset_jeu"
        temp = call_server(url, None)
        if temp:
            self.app.view.change_game_state(temp[0][0])

    def start_game_server(self):
        print("Starting game server...")
        url = self.urlserveur + "/creer_partie"
        params = {"nom": self.username}
        temp = call_server(url, params)
        if temp:
            self.app.view.change_game_state(temp[0][0])
            self.app.after(1000, self.update_lobby)

    def bind_server_buttons(self):
        self.app.view.connect_button.bind("<Button-1>", self.connect_to_server)
        self.app.view.restart_button.bind("<Button-1>", self.restart_server)

    def update_lobby(self):
        url = self.urlserveur + "/boucler_sur_lobby"
        params = {"nom": self.username}
        temp = call_server(url, params)
        if 'courante' in temp:
            self.start_game_signal(temp)
        else:
            self.joueurs = temp
            self.app.view.update_player_list(self.joueurs[0])
            self.after_id = self.app.after(1000, self.update_lobby)
            self.app.view.start_button.bind("<Button-1>",
                                            self.start_game_signal)

    def start_game_signal(self, _):
        self.app.after_cancel(self.after_id)

        self.start_game(self.joueurs)


def call_server(url, params):
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


if __name__ == "__main__":
    with Profile() as p:
        controller = Controller()
        controller.app.mainloop()

        Stats(p).sort_stats('cumtime').print_stats(20)
