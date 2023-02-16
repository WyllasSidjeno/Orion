import random
from tkinter import Tk, Frame, Label, Canvas, Entry, Button, Scrollbar

from view_template import hexDarkGrey, hexDark

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orion_modele import Modele as Model


class App(Tk):
    view: Frame

    def __init__(self, server_url, username):
        super().__init__()
        self.title("Orion - Space Strategy Game")
        self.view = ConnectionScreen(self, server_url, username)
        self.view.pack(fill="both", expand=True)

    def change_view(self, mod):
        self.view.destroy()
        self.minsize(720, 480)
        self.view = GameView(self, mod)
        self.view.pack(fill="both", expand=True)


class ConnectionScreen(Frame):
    def __init__(self, master, urlserveur: str, username: str):
        super().__init__(master)
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
        self.url_entry.insert(0, urlserveur)

        self.connect_button = Button(self, text="Connect")

        self.restart_button = Button(self, text="Restart")

        self.player_list = Canvas(self, width=300, height=100,
                                  bg=hexDarkGrey)

        self.start_button = Button(self, text="Start Game")

        # todo: change for the variables all the hard coded values

        self.place_all()

    def place_all(self):
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
    def __init__(self, master, mod):
        super().__init__(master)

        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=1280, height=720)

        self.top_bar = Frame(self, bg=hexDark, bd=1,
                             relief="solid")

        self.side_bar = Frame(self, bg=hexDark, bd=1,
                              relief="solid")

        self.scrollX = Scrollbar(self, orient="horizontal",
                                 background=hexDark)

        self.scrollY = Scrollbar(self, orient="vertical")

        self.canvas = Canvas(self, bg=hexDark, bd=1,
                             relief="solid", highlightthickness=0,
                             xscrollcommand=self.scrollX.set,
                             yscrollcommand=self.scrollY.set)

        self.scrollX.config(command=self.canvas.xview)
        self.scrollY.config(command=self.canvas.yview)

        self.configure_grid()
        self.create_background(mod.largeur, mod.hauteur)
        self.generate(mod)

    def configure_grid(self):
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
        self.canvas.grid(row=1, column=1, columnspan=9, rowspan=9,
                         sticky="nsew")

        self.scrollX.grid(row=9, column=1, columnspan=9, sticky="sew")
        self.scrollY.grid(row=1, column=9, rowspan=9, sticky="nse")

        self.scrollX.lift(self.canvas)
        self.scrollY.lift(self.canvas)

        self.canvas.configure(scrollregion=(0, 0, 9000, 9000))



    def create_background(self, x,y):
        for i in range(10000):
            x = random.randint(0, x)
            y = random.randint(0, y)
            n = random.randint(0, 3)
            col = random.choice(["LightYellow", "azure1", "pink"])
            self.canvas.create_oval(x, y, x + n, y + n, fill=col,
                                    tags="background")

    def generate(self, mod):
        self.generate_stars(mod.etoiles)
        self.generate_wormhole(mod.trou_de_vers)

    def generate_stars(self, stars):
       for star in stars :
              self.canvas.create_oval(star.x, star.y, star.x +
                                      star.taille, star.y + star.taille,
                                      fill="grey", tags="stars")

    def generate_wormhole(self, wormholes):
        for wormhole in wormholes:
            self.canvas.create_oval(wormhole.porte_a.x,
                                    wormhole.porte_a.y,
                                    wormhole.porte_a.x +
                                    wormhole.porte_a.pulse,
                                    wormhole.porte_a.y +
                                    wormhole.porte_a.pulse,
                                    fill=wormhole.porte_a.couleur,
                                    tags="wormhole")

            self.canvas.create_oval(wormhole.porte_b.x,
                                    wormhole.porte_b.y,
                                    wormhole.porte_b.x +
                                    wormhole.porte_b.pulse,
                                    wormhole.porte_b.y +
                                    wormhole.porte_b.pulse,
                                    fill=wormhole.porte_b.couleur,
                                    tags="wormhole")

    def horizontal_scroll(self, event):
        self.canvas.xview_scroll(-1 * int(event.delta / 120), "units")
        # will scroll left or right depending on the sign of the delta

    def vertical_scroll(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        # will scroll up or down depending on the sign of the delta


    def refresh(self, mod):
        pass
        #tags
