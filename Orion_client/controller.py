import json
import urllib
import urllib.error
import urllib.parse
import urllib.request
from random import random, seed

from Orion_client.view import App, GameView
from Orion_client.orion_modele import Modele as Model


class Controller():
    model: Model
    def __init__(self):
        self.username: str = "p1"
        self.actionsrecues: list[str] = []
        """Liste des actions reçues du serveur"""
        self.actionsenvoyees: list[str] = []
        """Liste des actions à envoyées au serveur"""
        self.urlserveur: str = "http://127.0.0.1:8000"

        self.app = App(self.urlserveur, self.username)

        self.bind_server_buttons()

        self.after_id = None



    def call_server(self, url, params):
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

    def connect_to_server(self, _):
        print("Connecting to server...")
        url = self.urlserveur+"/tester_jeu"
        params = {"username": self.username}
        temp = self.call_server(url, params)
        print(temp)
        if temp[0][0]:
            str = temp[0][0]
            self.app.view.change_game_state(str)
            if str == "dispo":
                self.start_game_server()
            elif str == "attente":
                pass

    def restart_server(self, _):
        print("Restarting server...")
        url = self.urlserveur+"/reset_jeu"
        temp = self.call_server(url, None)
        print(temp)
        if temp:
            self.app.view.change_game_state(temp[0][0])

    def start_game_server(self):
        print("Starting game server...")
        url = self.urlserveur + "/creer_partie"
        params = {"nom": self.username}
        temp = self.call_server(url, params)
        if temp:
            self.app.view.change_game_state(temp[0][0])
            self.app.after(1000, self.update_lobby)

    def bind_server_buttons(self):
        self.app.view.connect_button.bind("<Button-1>", self.connect_to_server)
        self.app.view.restart_button.bind("<Button-1>", self.restart_server)

    def update_lobby(self):
        url = self.urlserveur+"/boucler_sur_lobby"
        params = {"nom": self.username}
        temp = self.call_server(url, params)
        print(temp)
        if 'courante' in temp:
            self.start_game(temp)
        else:
            self.joueurs = temp
            self.app.view.update_player_list(self.joueurs[0])
            self.after_id = self.app.after(1000, self.update_lobby)
            self.app.view.start_button.bind("<Button-1>",
                                            self.start_game)

    def start_game(self, _):
        seed(12471)
        ## Stop the update_lobby loop
        self.app.after_cancel(self.after_id)
        listejoueurs = []
        for i in self.joueurs:
            listejoueurs.append(i[0])
        self.model = Model(self, listejoueurs)
        self.app.change_view(self.model)

        self.app.view.canvas.bind("<MouseWheel>",
                                  self.app.view.vertical_scroll)
        self.app.view.canvas.bind("<Control-MouseWheel>", self.app.
                                  view.horizontal_scroll)

        self.app.view.canvas.bind("<Button-1>", self.print_tags) # DEBUG
    def print_tags(self, event):
        print(self.app.view.canvas.gettags("current"))



if __name__ == "__main__":
    controller = Controller()
    controller.app.mainloop()