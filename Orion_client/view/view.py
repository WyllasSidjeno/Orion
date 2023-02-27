from tkinter import Tk, Frame, Label, Canvas, Entry, Button, Scrollbar

from Orion_client.view.view_template import hexDark, hexDarkGrey, GameCanvas, \
    Minimap, SideBar

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
                                            font=("Arial", 10))

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

        self.join_server_button = Button(self, text="Join server")

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

    def bind_server_buttons(self, join_server, restart_server,
                            connect_server, start_game_server,
                            update_username, update_url):
        self.join_server_button.config(command=join_server)

        self.restart_button.config(command=restart_server)
        self.connect_button.config(command=connect_server)

        self.start_button.config(command=start_game_server)

        # The labels
        self.player_name_entry.bind("<Return>", update_username)
        self.url_entry.bind("<Return>", update_url)

    def disable_join_server_button(self):
        self.join_server_button.config(state="disabled")
        self.restart_button.config(state="normal")
        self.connect_button.config(state="normal")

    def disable_restart_connect_button(self):
        self.restart_button.config(state="disabled")
        self.connect_button.config(state="disabled")

        self.start_button.config(state="normal")


class GameView(Frame):
    def __init__(self):
        super().__init__()

        self.config(bg=hexDark, bd=2, relief="solid",
                    width=1280, height=720)

        self.top_bar = Frame(self, bg=hexDark, bd=1, relief="solid")
        """Représente la barre du haut de la vue du jeu."""

        self.side_bar = SideBar(self)
        """Représente la barre de droite de la vue du jeu."""

        self.scrollX = Scrollbar(self, orient="horizontal")
        """Représente la scrollbar horizontale de la vue du jeu."""
        self.scrollY = Scrollbar(self, orient="vertical")
        """""Représente la scrollbar verticale de la vue du jeu."""

        self.canvas = GameCanvas(self, self.scrollX, self.scrollY)
        """Représente le canvas de la vue du jeu."""

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

    def refresh(self, mod):
        self.canvas.refresh(mod)
        self.side_bar.refresh(mod)

    def initialize(self, mod):
        self.configure_grid()
        self.canvas.initialize(mod)
        self.side_bar.initialize(mod)

        self.side_bar.minimap.bind("<Button-1>",
                                   self.on_minimap_click)

        self.canvas.bind("<MouseWheel>",
                         self.canvas.vertical_scroll)
        self.canvas.bind("<Control-MouseWheel>",
                         self.canvas.horizontal_scroll)

        self.canvas.bind("<Button-1>", self.get_xy)  # DEBUG

    def on_minimap_click(self, event) -> None:
        """Event handler for minimap click

        Moves the view to the clicked position"""
        self.canvas.xview_moveto(event.x /
                                 self.side_bar.minimap.winfo_width())
        self.canvas.yview_moveto(event.y /
                                 self.side_bar.minimap.winfo_height())

    def get_xy(self, event) -> None:
        """Get xy coordinates on click"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        print("x: {}, y: {}".format(x, y))
