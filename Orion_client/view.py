from tkinter import Tk, Frame, Label, Canvas, Entry, Button

from view_template import hexDarkGrey, hexDark


class App(Tk):
    current_frame: Frame

    def __init__(self, parent, url_serveur, username, msg_initial):
        super().__init__()
        self.title("Orion - Space Strategy Game")

    def change_frame(self, frame):
        """Allows to change from one frame to another, like connection
        screen and game screen"""
        self.current_frame = frame
        # auto resize the window to the size of the frame
        self.current_frame.pack(fill="both", expand=True)


class GameView(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=300, height=300)


class ConnectionScreen(Frame):
    def __init__(self, master):
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

        self.url_serveur_label = Label(self, text="URL serveur: ",
                                        bg=hexDark, fg="white",
                                        font=("Arial", 10))
        self.url_entry = Entry(self, width=30)
        self.url_entry.insert(0, "http://localhost:5000")

        self.connect_button = Button(self, text="Connect")
        self.connect_button.place(anchor="center", relx=0.5, rely=0.5)

        self.player_list = Canvas(self, width=300, height=100,
                                    bg=hexDarkGrey)
        self.player_list.place(anchor="center", relx=0.5, rely=0.7)

        player_list = {"player1": "ready", "player2": "not ready",
                       "player3": "ready", "player4": "not ready",}
        for i, player in enumerate(player_list):
            player_name = Label(self.player_list, text=player,
                                bg=hexDarkGrey, fg="white",
                                font=("Arial", 10))
            player_name.place(anchor="w", relx=0.1, rely=0.2 + i * 0.2)
            player_state = Label(self.player_list, text=player_list[player],
                                 bg=hexDarkGrey, fg="white",
                                 font=("Arial", 10))
            player_state.place(anchor="w", relx=0.7, rely=0.2 + i * 0.2)

        self.start_button = Button(self, text="Start Game")
        self.start_button.place(anchor="center", relx=0.5, rely=0.9)

        # todo: change for the variables all the hard coded values

        self.place_all()

    def place_all(self):
        self.connection_screen_label.place(anchor="center", relx=0.5,
                                           rely=0.1)
        self.game_state_label.place(anchor="center", relx=0.35, rely=0.2)
        self.game_state_label_value.place(anchor="center", relx=0.58,
                                          rely=0.2)

        self.player_name_label.place(anchor="center", relx=0.32, rely=0.3)
        self.player_name_entry.place(anchor="center", relx=0.55, rely=0.3)

        self.url_serveur_label.place(anchor="center", relx=0.325, rely=0.4)
        self.url_entry.place(anchor="center", relx=0.55, rely=0.4)

        self.connect_button.place(anchor="center", relx=0.5, rely=0.5)




if __name__ == "__main__":
    app = App(None, None, None, None)

    splash_screen = ConnectionScreen(app)
    game_view = GameView(app)
    app.change_frame(splash_screen)

    app.mainloop()
