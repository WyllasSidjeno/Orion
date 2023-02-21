from tkinter import Tk, Frame, Label, Canvas, Entry, Button, Scrollbar

from Orion_client.view.view_template import hexDark, hexDarkGrey, GameCanvas, \
    Minimap

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Orion_client.model import Model


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
                                            font=("Arial", 15))

        self.player_name_label = Label(self, text="Player name: ",
                                       bg=hexDark, fg="white",
                                       font=("Arial", 10))
        self.player_name_entry = Entry(self, width=30)
        self.player_name_entry.insert(0, username)

        self.url_serveur_label = Label(self, text="URL serveur: ",
                                       bg=hexDark, fg="white",
                                       font=("Arial", 10))
        self.url_entry = Entry(self, width=30)
        self.url_entry.insert(0, url_serveur)

        self.connect_button = Button(self, text="Connect")

        self.restart_button = Button(self, text="Restart")

        self.player_list = Canvas(self, width=300, height=100,
                                  bg=hexDarkGrey)

        self.start_button = Button(self, text="Start Game")

        # todo: change for the variables all the hard coded values

    def show(self):
        self.pack(fill="both", expand=True)

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

        self.connect_button.place(anchor="center",
                                  relx=0.45, rely=0.5)
        self.restart_button.place(anchor="center",
                                  relx=0.55, rely=0.5)

        self.player_list.place(anchor="center", relx=0.5, rely=0.7)

        self.start_button.place(anchor="center", relx=0.5, rely=0.9)

    def change_game_state(self, state):
        if state == "courante":
            self.game_state_label_value.config(text="Game started")
        else:
            self.game_state_label_value.config(text=state)

    def update_player_list(self, joueurs):
        for i in self.player_list.winfo_children():
            i.destroy()
        for i, player in enumerate(joueurs):
            if not player == 0:
                player_name = Label(self.player_list, text=player,
                                    bg=hexDarkGrey, fg="white",
                                    font=("Arial", 10))
                player_name.place(anchor="w", relx=0.5, rely=0.2 + i * 0.2)


class GameView(Frame):
    def __init__(self):
        super().__init__()

        self.config(bg=hexDark, bd=2, relief="solid",
                    width=1280, height=720)

        self.top_bar = Frame(self, bg=hexDark, bd=1, relief="solid")
        """Représente la barre du haut de la vue du jeu."""

        self.side_bar = Frame(self, bg=hexDark, bd=1, relief="solid")
        """Représente la barre de droite de la vue du jeu."""

        self.scrollX = Scrollbar(self, orient="horizontal")
        """Représente la scrollbar horizontale de la vue du jeu."""

        self.scrollY = Scrollbar(self, orient="vertical")
        """""Représente la scrollbar verticale de la vue du jeu."""

        self.canvas = GameCanvas(self, self.scrollX, self.scrollY)
        """Représente le canvas de la vue du jeu."""

        self.planet_frame = Frame(self.side_bar, bg=hexDark, bd=1,
                                  relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.planet_label = Label(self.planet_frame, text="Planet",
                                  bg=hexDark, fg="white",
                                  font=("Arial", 20))
        """Représente le label de la vue du jeu contenant les informations"""

        self.armada_frame = Frame(self.side_bar, bg=hexDark, bd=1,
                                  relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.armada_label = Label(self.armada_frame, text="Armada",
                                  bg=hexDark, fg="white",
                                  font=("Arial", 20))
        """Représente le label de la vue du jeu contenant les informations"""

        self.minimap_frame = Frame(self.side_bar, bg=hexDark, bd=1,
                                   relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.minimap_label = Label(self.minimap_frame, text="Minimap",
                                   bg=hexDark, fg="white",
                                   font=("Arial", 20))
        """Représente le label de la vue du jeu contenant les informations"""
        self.minimap = Minimap(self.minimap_frame)
        """Représente le lbel de la vue du jeu contenant les informations"""

        self.configure_grid()

        self.pack(fill="both", expand=True)

    def configure_grid(self):
        """Configures the grid of the game view."""
        self.grid_propagate(False)
        for i in range(10):
            if i == 0 or i == 1:
                self.grid_columnconfigure(i, weight=1, minsize=50)
            self.grid_columnconfigure(i, weight=1)
        for i in range(10):
            if i == 0:
                self.grid_rowconfigure(i, weight=1, minsize=50)
            self.grid_rowconfigure(i, weight=1)

        self.top_bar.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.side_bar.grid(row=1, column=0, rowspan=9, sticky="nsew")
        self.side_bar.grid_propagate(False)
        self.canvas.grid(row=1, column=1, columnspan=9, rowspan=9,
                         sticky="nsew")

        self.scrollX.grid(row=9, column=1, columnspan=9, sticky="sew")
        self.scrollY.grid(row=1, column=9, rowspan=9, sticky="nse")

        self.scrollX.lift(self.canvas)  # todo: check if it's necessary
        self.scrollY.lift(self.canvas)  # todo: check if it's necessary

        for i in range(3):
            self.side_bar.grid_rowconfigure(i, weight=1)
        self.side_bar.grid_columnconfigure(0, weight=1)

        self.planet_frame.grid(row=0, column=0, sticky="nsew")
        self.planet_label.place(anchor="center", relx=0.5, rely=0.1)
        self.armada_frame.grid(row=1, column=0, sticky="nsew")
        self.armada_label.place(anchor="center", relx=0.5, rely=0.1)
        self.minimap_frame.grid(row=2, column=0, sticky="nsew")

        self.minimap_label.place(anchor="center", relx=0.5, rely=0.1)
        # Give it a dynamic size
        self.minimap.place(anchor="n", relx=0.5, rely=0.3, relwidth=0.9,
                           relheight=0.5)

        # self.minimap_label.place(anchor="center", relx=0.5, rely=0.1)
        # self.minimap.place(anchor="n", relx=0.5, rely=0.28)

    def refresh(self, mod):
        self.canvas.refresh(mod)

    def initialize(self, mod):
        self.canvas.initialize(mod)
        self.minimap.initialize(mod)

        self.minimap.bind("<Button-1>",
                          self.on_minimap_click)

        self.canvas.bind("<MouseWheel>",
                         self.canvas.vertical_scroll)
        self.canvas.bind("<Control-MouseWheel>",
                         self.canvas.horizontal_scroll)

        self.canvas.bind("<Button-1>", self.print_tags)  # DEBUG

    def on_minimap_click(self, event) -> None:
        """Event handler for minimap click

        Moves the view to the clicked position"""
        self.canvas.xview_moveto(event.x /
                                 self.minimap.winfo_width())
        self.canvas.yview_moveto(event.y /
                                 self.minimap.winfo_height())

    def print_tags(self, _) -> None:
        """Print the tags of the current object"""
        print(self.canvas.gettags("current"))
        # xy
        print(self.canvas.coords("current"))
