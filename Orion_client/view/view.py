from tkinter import Frame, Label, Canvas, Entry, Button, Scrollbar

from helpers.CommandQueues import ControllerQueue
from view.ui_template import GameCanvas, SideBar, Hud, ChatBox

from view.ui_template import Color

from science import ArbreScience


class GameView(Frame):
    id: str
    command_queue: ControllerQueue

    def __init__(self, command_queue: ControllerQueue, username):
        super().__init__()
        """Représente la queue de commandes du jeu."""
        self.config(bg=Color.dark.value, bd=2, relief="solid",
                    width=1280, height=720)

        self.command_queue = command_queue

        self.hud = Hud(self)
        """Représente la barre du haut de la vue du jeu."""
        self.side_bar = SideBar(self)
        """Représente la barre de droite de la vue du jeu."""
        self.canvas = GameCanvas(self, username)
        """Représente le canvas de la vue du jeu."""

        self.chat = ChatBox(self, command_queue)

        self.pack(fill="both", expand=True)
        self.fenetre_science = ArbreScience(self)

        self.sciences = {}

        self.canvas.etoile_window.construct_ship_menu.register_command_queue(
            command_queue)

        self.canvas.etoile_window.construct_building_menu.register_command_queue(
            command_queue)

       # self.canvas.science_window.show_science() todo : à implémenter avec la science (vérifier les paramètres)

        # todo : à déplacer dans le constructeur de la fenêtre

        self.bind_game_requests()  # todo : à déplacer dans le constructeur de la fenêtre

        self.canvas.etoile_window.proprietaire_label.config(
            text=username)  # todo : à déplacer dans le constructeur de la fenêtre

        self.configure_grid()

        self.focus_set()

        self.bind("<Return>",
                  self.chat.show)  # todo : à déplacer dans le constructeur de la fenêtre

        self.science_menu = ArbreScience(self)
        self.hud.science_button.bind("<Button-1>", self.affichage_science)

    def affichage_science(self, event):
        self.fenetre_science.show_science(event, self.sciences)

    def configure_grid(self):
        """Configures la grid de la vue principale du jeu."""
        self.grid_propagate(False)
        for i in range(10):
            self.grid_columnconfigure(i, weight=1,
                                      minsize=50 if i < 2 else None)

            self.grid_rowconfigure(i, weight=1,
                                   minsize=50 if i == 0 else None)

        self.hud.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.side_bar.grid(row=1, column=0, rowspan=9, sticky="nsew")
        self.canvas.grid(row=1, column=1, columnspan=9, rowspan=9,
                         sticky="nsew")

    def bind_game_requests(self):
        """Binds les fonctions de la vue du jeu aux evenements du canvas."""
        self.side_bar.minimap.bind("<Button-1>",
                                   self.on_minimap_click)
        self.canvas.bind("<Button-1>", self.on_game_click)
        self.canvas.bind("<Button-3>", self.on_game_click)

    def refresh(self, mod):
        """Refresh la vue du jeu."""
        self.canvas.refresh(mod)
        self.side_bar.refresh(mod)

        dict_ress = mod.joueurs[mod.controller_username].ressources
        dict_ress.pop(
            "science")

        self.hud.update_ressources(**dict_ress)
        self.chat.refresh(mod)

        self.side_bar.minimap.user_square_move(
            self.canvas.bounding_box.__tuple__())

        self.sciences = mod.joueurs[mod.controller_username].sciences_status

    def on_minimap_click(self, event) -> None:
        """ Bouge le canvas vers la position du clic sur la minimap."""
        pctx = event.x / self.side_bar.minimap.winfo_width()
        """Percentage of the x coordinate on the minimap."""
        pcty = event.y / self.side_bar.minimap.winfo_height()
        """Percentage of the y coordinate on the minimap."""

        # make it so that the canvas is centered on the click cursor, not the top left corner
        pctx -= 0.05
        pcty -= 0.05


        self.canvas.move_to(pctx, pcty)

    def on_game_click(self, event) -> None:
        """Gère les clics sur le canvas.

        Elle s'occupe de gérer les clics sur le canvas et d'afficher
        les fenetres demandés au clic. De plus,
        elle envoie les commandes au controller pour traiter les clics.
        """
        self.canvas.scan_mark(event.x, event.y)
        if self.canvas.etoile_window.is_visible:
            self.canvas.etoile_window.hide()

        pos = self.canvas.canvasx(event.x) + self.canvas.bounding_box.x,\
            self.canvas.canvasy(event.y) + self.canvas.bounding_box.y
        tags_list = []
        for tag in self.canvas.gettags("current"):
            tags_list.append(tag)

        if event.num == 3:
            self.command_queue.handle_right_click(pos, tags_list)
        elif event.num == 1:
            self.command_queue.handle_left_click(pos, tags_list)


class LobbyView(Frame):
    def __init__(self, url_serveur: str, username: str):
        super().__init__()
        self.config(bg=Color.dark.value, bd=2,
                    relief="solid",
                    width=620, height=480)

        self.connection_screen_label = Label(self,
                                             text='Orion - '
                                                  'Connection screen',
                                             bg=Color.dark.value, fg="white",
                                             font=("Fixedsys", 30))

        self.game_state_label = Label(self, text="Game state:",
                                      bg=Color.dark.value, fg="white",
                                      font=("Fixedsys", 15))
        self.game_state_label_value = Label(self, text="Not connected",
                                            bg=Color.dark.value, fg="white",
                                            font=("Fixedsys", 10))

        self.player_name_label = Label(self, text="Joueur name: ",
                                       bg=Color.dark.value, fg="white",
                                       font=("Fixedsys", 10))
        self.player_name_entry = Entry(self, width=30)
        self.player_name_entry.insert(0, username)

        self.url_serveur_label = Label(self, text="URL serveur: ",
                                       bg=Color.dark.value, fg="white",
                                       font=("Fixedsys", 10))
        self.url_entry = Entry(self, width=30)
        self.url_entry.insert(0, url_serveur)

        self.join_server_button = Button(self, text="Join server")

        self.connect_button = Button(self, text="Connect")

        self.restart_button = Button(self, text="Restart")

        self.player_list = Canvas(self, width=300, height=100,
                                  bg=Color.dark.value)

        self.start_button = Button(self, text="Start Game")

        # todo: change for the variables all the hard coded values

    def initialize(self):
        self.connection_screen_label.place(anchor="center",
                                           relx=0.5, rely=0.1)

        self.game_state_label.place(anchor="center",
                                    relx=0.35, rely=0.2)
        self.game_state_label_value.place(anchor="center",
                                          relx=0.58, rely=0.2)

        self.player_name_label.place(anchor="center",
                                     relx=0.32, rely=0.3)
        self.player_name_entry.place(anchor="center",
                                     relx=0.55, rely=0.3)

        self.url_serveur_label.place(anchor="center",
                                     relx=0.325, rely=0.4)
        self.url_entry.place(anchor="center",
                             relx=0.55, rely=0.4)

        self.join_server_button.place(anchor="center",
                                      relx=0.5, rely=0.5)

        self.connect_button.place(anchor="center",
                                  relx=0.35, rely=0.50)
        self.connect_button.config(state="disabled")

        self.restart_button.place(anchor="center",
                                  relx=0.65, rely=0.50)
        self.restart_button.config(state="disabled")

        self.player_list.place(anchor="center", relx=0.5, rely=0.7)

        self.start_button.place(anchor="center", relx=0.5, rely=.85)
        self.start_button.config(state="disabled")

    def bind_server_buttons(self, join_server, restart_server,
                            connect_server, start_game_server,
                            update_username, update_url):
        pass
        self.join_server_button.config(command=join_server)

        self.restart_button.config(command=restart_server)
        self.connect_button.config(command=connect_server)

        self.start_button.config(command=start_game_server)

        # The labels
        self.player_name_entry.bind("<Return>", update_username)
        self.url_entry.bind("<Return>", update_url)

    def show(self):
        self.pack(fill="both", expand=True)

    def change_game_state(self, state):
        if state == "courante":
            self.game_state_label_value.config(text="Game started")
        else:
            self.game_state_label_value.config(text=state)

    def update_player_list(self, joueurs):
        for i in self.player_list.winfo_children():
            i.destroy()
        if joueurs:
            # Remove the ints from the list
            joueurs = [x for x in joueurs if not isinstance(x, int)]

            for i in range(len(joueurs)):
                Label(self.player_list, text=joueurs[i][0],
                      bg=Color.dark.value, fg="white",
                      font=("Fixedsys", 10)).place(anchor="center",
                                                   relx=0.5,
                                                   rely=0.15 + i * 0.2)

    def enable_restart_button(self):
        self.restart_button.config(state="normal")

    def enable_connect_button(self):
        self.connect_button.config(state="normal")

    def enable_start_game_button(self):
        self.start_button.config(state="normal")

    def disable_join_server_button(self):
        self.join_server_button.config(state="disabled")

    def disable_restart_connect_button(self):
        self.restart_button.config(state="disabled")
        self.connect_button.config(state="disabled")
