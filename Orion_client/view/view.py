from tkinter import Frame, Label, Canvas, Entry, Button, Scrollbar

from Orion_client.view.view_template import hexDark, hexDarkGrey, GameCanvas, \
    SideBar


class GameView(Frame):
    nom: str
    id: str

    def __init__(self, command):
        super().__init__()
        self.command_queue = command
        """Représente la queue de commandes du jeu."""

        self.config(bg=hexDark, bd=2, relief="solid",
                    width=1280, height=720)

        self.top_bar = Frame(self, bg=hexDark, bd=1, relief="solid")
        """Représente la barre du haut de la vue du jeu."""

        self.side_bar = SideBar(self, self.command_queue)
        """Représente la barre de droite de la vue du jeu."""

        self.scrollX = Scrollbar(self, orient="horizontal")
        """Représente la scrollbar horizontale de la vue du jeu."""
        self.scrollY = Scrollbar(self, orient="vertical")
        """""Représente la scrollbar verticale de la vue du jeu."""

        self.canvas = GameCanvas(self, self.scrollX, self.scrollY,
                                 self.command_queue)
        """Représente le canvas de la vue du jeu."""

        self.previous_selection: list[str] | None = None
        """Représente la sélection précédente de l'utilisateur dans la vue."""

        self.pack(fill="both", expand=True)

        self.bind_game_requests()

    def configure_grid(self):
        """Configures la grid de la vue principale du jeu."""
        self.grid_propagate(False)
        for i in range(10):
            self.grid_columnconfigure(i, weight=1,
                                      minsize=50 if i < 2 else None)

            self.grid_rowconfigure(i, weight=1,
                                   minsize=50 if i == 0 else None)

        self.top_bar.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.side_bar.grid(row=1, column=0, rowspan=9, sticky="nsew")
        self.side_bar.grid_propagate(False)
        self.canvas.grid(row=1, column=1, columnspan=9, rowspan=9,
                         sticky="nsew")

        self.scrollX.grid(row=9, column=1, columnspan=9, sticky="sew")
        self.scrollY.grid(row=1, column=9, rowspan=9, sticky="nse")

    def initialize(self, mod, username: str, user_id: str):
        """Initialise la vue du jeu apres son lancement et lors de la
        reception du modele."""
        self.nom = username
        self.id = user_id

        self.configure_grid()
        self.canvas.initialize(mod)
        self.side_bar.initialize(mod)
        self.canvas.planet_window.initialize()

    def bind_game_requests(self):
        """Binds les fonctions de la vue du jeu aux evenements du canvas."""
        self.side_bar.minimap.bind("<Button-1>",
                                   self.on_minimap_left_click)

        self.canvas.bind("<MouseWheel>",
                         self.canvas.vertical_scroll)
        self.canvas.bind("<Control-MouseWheel>",
                         self.canvas.horizontal_scroll)

        self.canvas.bind("<Button-1>", self.on_game_left_click)
        self.canvas.bind("<Button-3>", self.on_game_right_click)

    def refresh(self, mod):
        """Refresh la vue du jeu."""
        self.canvas.refresh(mod)
        self.side_bar.refresh(mod)

    def on_minimap_left_click(self, event) -> None:
        """ Bouge le canvas vers la position du clic sur la minimap."""
        pctx = event.x / self.side_bar.minimap.winfo_width()
        """Percentage of the x coordinate on the minimap."""
        pcty = event.y / self.side_bar.minimap.winfo_height()
        """Percentage of the y coordinate on the minimap."""

        x = (self.canvas.winfo_width() / 2) / 9000
        """ This represents the x coordinate of the center of the canvas"""
        y = (self.canvas.winfo_height() / 2) / 9000
        """ This represents the y coordinate of the center of the canvas"""

        self.canvas.move_to((pctx - x), (pcty - y))

    def on_game_left_click(self, event) -> None:
        """ Gère les interactions de la vue du jeu lors d'un clic gauche."""

        pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        tags_list = []
        for tag in self.canvas.gettags("current"):
            tags_list.append(tag)

        self.look_for_etoile_window_interactions(tags_list)

        self.look_for_ship_interactions(tags_list, pos)

    def look_for_etoile_window_interactions(self, tags_list: list[str]):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        une etoile dans le canvas."""
        print("etoile", tags_list)
        if self.canvas.planet_window.is_shown:
            self.canvas.planet_window.hide()
        elif self.is_owner_and_is_type(tags_list, "etoile_occupee"):
            self.canvas.planet_window.show(tags_list[1])

    def look_for_ship_interactions(self, tags_list: list[str],
                                   pos: tuple[int, int]):
        """Gère les interactions de la vue du jeu lors d'un clic gauche sur
        un vaisseau dans le canvas sur la selection actuelle et la selection
        précédente."""
        if self.is_owner_and_is_type(tags_list, "vaisseau"):
            print("ship", tags_list[1])
            if self.previous_selection is None:
                print("previous selection is none")
                self.previous_selection = tags_list
        elif self.previous_selection is not None:
            print("ship movement request")
            self.command_queue.add(self.nom, "ship_target_change_request",
                                   self.previous_selection[1], pos)
            self.previous_selection = None

    def on_game_right_click(self, _):
        """Gère les interactions de la vue du jeu lors d'un clic droit."""
        if self.canvas.planet_window.is_shown:
            self.canvas.planet_window.hide()
        tags_list = []
        for tag in self.canvas.gettags("current"):
            tags_list.append(tag)

        if self.previous_selection:
            if self.is_type(self.previous_selection, "vaisseau"):
                if self.is_type(tags_list, ["etoile_occupee", "etoile"]) \
                        and not self.is_owner(tags_list):
                    print("ship movement request to star")
            self.previous_selection = None

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
        return self.id in tags_list or self.nom in tags_list

    def cancel_previous_selection(self):
        """Annule la selection précédente."""
        self.previous_selection = None


class LobbyView(Frame):
    def __init__(self, url_serveur: str, username: str):
        super().__init__()
        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=600, height=480)

        self.connection_screen_label = Label(self,
                                             text='Orion - '
                                                  'Connection screen',
                                             bg=hexDark, fg="white",
                                             font=("Arial", 30))

        self.game_state_label = Label(self, text="Game state:",
                                      bg=hexDark, fg="white",
                                      font=("Arial", 15))
        self.game_state_label_value = Label(self, text="Not connected",
                                            bg=hexDark, fg="white",
                                            font=("Arial", 10))

        self.player_name_label = Label(self, text="Joueur name: ",
                                       bg=hexDark, fg="white",
                                       font=("Arial", 10))
        self.player_name_entry = Entry(self, width=30)
        self.player_name_entry.insert(0, username)

        self.url_serveur_label = Label(self, text="URL serveur: ",
                                       bg=hexDark, fg="white",
                                       font=("Arial", 10))
        self.url_entry = Entry(self, width=30)
        self.url_entry.insert(0, url_serveur)

        self.join_server_button = Button(self, text="Join server")

        self.connect_button = Button(self, text="Connect")

        self.restart_button = Button(self, text="Restart")

        self.player_list = Canvas(self, width=300, height=100,
                                  bg=hexDarkGrey)

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
                      bg=hexDarkGrey, fg="white",
                      font=("Arial", 10)).place(anchor="center",
                                                relx=0.5, rely=0.15 + i * 0.2)

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
