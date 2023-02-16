import random
from tkinter import Tk, Frame, Label, Canvas, Entry, Button, Scrollbar, \
    HORIZONTAL, VERTICAL

from Orion_client.orion_modele import Etoile
from view_template import hexDarkGrey, hexDark


class App(Tk):
    view: Frame

    def __init__(self, server_url, username):
        super().__init__()
        self.title("Orion - Space Strategy Game")
        self.view = ConnectionScreen(self, server_url, username)
        self.view.pack(fill="both", expand=True)

    def change_view(self, view, master):
        self.view.destroy()
        self.minsize(720, 480)
        self.view = view(master)
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
    def __init__(self, master):
        super().__init__(master)

        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=1280, height=720)

        self.top_bar = Frame(self, bg=hexDark, bd=1,
                             relief="solid")

        self.side_bar = Frame(self, bg=hexDark, bd=1,
                              relief="solid")

        self.scrollX = Scrollbar(self, orient="horizontal",
                                 background=hexDark, width=0)

        self.scrollY = Scrollbar(self, orient="vertical", width=0)

        self.canvas = Canvas(self, bg=hexDark, bd=1,
                             relief="solid", highlightthickness=0,
                             xscrollcommand=self.scrollX.set,
                             yscrollcommand=self.scrollY.set)

        self.scrollX.config(command=self.canvas.xview)
        self.scrollY.config(command=self.canvas.yview)

        self.configure_grid()
        self.show_game("assets/map1.txt")

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

        # make the canvas bigger to try the scroll
        self.canvas.configure(scrollregion=(0, 0, 9000, 9000))

    def show_game(self, mod):
        self.show_stars(mod)
        # self.show_planets(mod)

    def show_stars(self, mod):
        for i in range(10000):
            x = random.randint(0, 9000)
            y = random.randint(0, 9000)
            n = random.randint(0, 3)
            col = random.choice(["LightYellow", "azure1", "pink"])
            self.canvas.create_oval(x, y, x + n, y + n, fill=col,
                                    tags="background")

    def show_planets(self, etoiles):
        for etoile in etoiles:
            self.canvas.create_oval(etoile.x, etoile.y,
                                    etoile.x + etoile.rayon,
                                    etoile.y + etoile.rayon,
                                    fill=etoile.couleur,
                                    tags=(
                                    "etoile", etoile.proprietaire, etoile.id))
            # todo : minimap, joueur


if __name__ == "__main__":
    app = App("127.0.0.1", "Jean")
    app.view.connect_button.config(
        command=lambda: app.change_view(GameView, app))
    app.mainloop()
