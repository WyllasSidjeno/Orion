import json
import urllib
import urllib.error
import urllib.parse
import urllib.request

from Orion_client.view import App
from Orion_client.orion_modele import Modele as Model


class Controller():
    def __init__(self):
        self.username: str = "p1"
        self.actionsrecues: list[str] = []
        """Liste des actions reçues du serveur"""
        self.actionsenvoyees: list[str] = []
        """Liste des actions à envoyées au serveur"""
        self.urlserveur: str = "http://127.0.0.1:8000"

        self.app = App(self.urlserveur, self.username)

        self.bind_server_buttons()
        self.update_lobby()

    def connect_to_server(self, _):
        print("Connecting to server...")
        url = self.urlserveur+"/tester_jeu"
        params = {"username": self.username}
        temp = self.call_server(url, params)
        print(temp)
        if temp:
            self.app.view.change_game_state(temp[0][0])

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

    def restart_server(self, _):
        print("Restarting server...")
        url = self.urlserveur+"/reset_jeu"
        temp = self.call_server(url, None)
        print(temp)
        if temp:
            self.app.view.change_game_state(temp[0][0])

    def bind_server_buttons(self):
        self.app.view.connect_button.bind("<Button-1>", self.connect_to_server)

        self.app.view.restart_button.bind("<Button-1>", self.restart_server)

    def update_lobby(self):
        url = self.urlserveur+"/boucler_sur_lobby"
        params = {"nom": self.username}
        temp = self.call_server(url, params)
        if 'courante' in temp:
            self.start_game(temp)
        else:
            self.joueurs = temp
            self.app.view.update_player_list(self.joueurs)
            self.app.after(1000, self.update_lobby)

    def start_game(self, temp):
        pass







if __name__ == "__main__":
    controller = Controller()
    controller.app.mainloop()