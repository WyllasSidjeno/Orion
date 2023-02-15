from tkinter import Frame, Label, Canvas
from typing import Any

hexDarkGrey = "#36393f"
hexDark = "#2f3136"


class PlanetWindow(Frame):
    """Fenetre qui affiche les informations d'une planete"""
    population_canvas: Canvas
    population_label: Label
    name_label: Label
    owner_label: Label
    building_label: Label
    stockpile_boolean_label: Label

    def __init__(self, parent: Any, **kwargs):
        """Initialise la fenetre"""
        super().__init__(parent, **kwargs)
        self.planetInfo: dict[str, dict[str, int | Any]] = {
            # todo : Any building
            "header": {
                "name": "Mars",
                "owner": "Joueur 1",
                "population": 1000
            },
            "output": {
                "Metal": 5,
                "Beton": 5,
                "Energie": 5,
                "Nourriture": 5
            },
            "building": {
                "b1",
                "b2",
                "b3",
                "b4",
                "b5",
                "b6",
            }
        }
        self.headerFrame: Frame = \
            Frame(self, bg=hexDarkGrey, bd=1, relief="solid")
        self.mainFrame: Frame = Frame(self, bg=hexDarkGrey, bd=1,
                                      relief="solid")
        self.sideFrame = Frame(self, bg=hexDarkGrey, bd=1, relief="solid")

        self.create_layout(self.planetInfo)

    def create_layout(self, planet_info) -> None:
        """Crée le layout de la fenetre, c'est à dire les frames et les
        widgets"""
        self.configure(bg="dark grey", width=400, height=400)

        self.create_header(planet_info["header"])
        self.create_main(planet_info["building"])
        self.create_side(planet_info["output"])

    def create_header(self, planet_info) -> None:
        """Crée le header de la fenetre, la ou les informations identifiante
        de la planete sont affichées

        :param planet_info: Dictionnaire contenant
        les informations de la planete
        """
        # Start with the header frame
        self.headerFrame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        # Create the widgets and place them
        # # Name
        self.owner_label = Label(self.headerFrame, text=planet_info["owner"],
                                 bg=hexDarkGrey, fg="white",
                                 font=("Arial", 15))
        self.owner_label.place(anchor="center", relx=0.12, rely=0.2)

        # # Population Canvas
        self.population_canvas = Canvas(self.headerFrame, bg=hexDarkGrey,
                                        width=51, height=51,
                                        highlightthickness=0)
        self.population_canvas.place(anchor="center", relx=0.85, rely=0.45)
        # # # Population label
        self.population_canvas.create_oval(0, 0, 50, 50, fill="dark green")
        self.population_label = Label(self.population_canvas,
                                      text=planet_info["population"],
                                      bg="dark green", fg="white",
                                      font=("Arial", 8))
        self.population_label.place(anchor="center", relx=0.5, rely=0.5)

        # # Owner
        self.name_label = Label(self.headerFrame, text=planet_info["name"],
                                bg=hexDarkGrey, fg="white",
                                font=("Arial", 20))
        self.name_label.place(anchor="center", relx=0.1, rely=0.7)

    def create_main(self, planet_info) -> None:
        """Crée le main de la fenetre, là ou les bâtiments sont affichés

        :param planet_info: Dictionnaire contenant"""
        # Start with the main frame
        self.mainFrame.place(relx=0, rely=0.2, relwidth=0.60, relheight=0.8)

        # Create the widgets and place them
        # # Building label
        self.building_label = Label(self.mainFrame, text="Batiments",
                                    bg=hexDarkGrey, fg="white",
                                    font=("Arial", 13))

        self.building_label.place(anchor="center", relx=0.5, rely=0.05)

        # # Building grid
        building_grid = Frame(self.mainFrame, bg=hexDarkGrey)
        building_grid.place(relx=0.1, rely=0.1, relwidth=0.8,
                            relheight=0.9)

        # # Building frames (depending on the number of buildings)
        for i, building in enumerate(planet_info):
            setattr(self, f"{building}_frame",
                    BuildingWindow(building_grid))
            if i % 2 == 0:  # If the building is on the left
                getattr(self,
                        f'{building}_frame').grid(row=i // 2, column=0,
                                                  padx=10, pady=10)
            else:  # If the building is on the right
                getattr(self,
                        f'{building}_frame').grid(row=i // 2, column=1,
                                                  padx=10, pady=10)

    def create_side(self, planet_info) -> None:
        """Crée le side de la fenetre, là oú le rendement de la planete est
        affiché"""

        # Start with the side frame
        self.sideFrame.place(relx=0.60, rely=0.2, relwidth=0.40, relheight=0.8)

        # Create the widgets and place them
        # # Ressource label
        ressource_label = Label(self.sideFrame, text="Ressources",
                                bg=hexDarkGrey, fg="white",
                                font=("Arial", 13))
        ressource_label.place(anchor="center", relx=0.5, rely=0.05)

        # # Ressource labels
        for i, ressource in enumerate(planet_info):
            setattr(self, f"{ressource}_label",
                    Label(self.sideFrame,
                          text=ressource + " : " + str(planet_info[ressource]),
                          bg=hexDarkGrey, fg="white", font=("Arial", 10)))

            getattr(self, f"{ressource}_label").place(anchor="center",
                                                      relx=0.5,
                                                      rely=0.13 + i * 0.1)

        # # Line separator
        line = Frame(self.sideFrame, bg="white", bd=1, relief="solid")
        line.place(relx=0.1, rely=0.5, relwidth=0.8, relheight=0.01)

        # # Other label
        other_label = Label(self.sideFrame, text="Autre",
                            bg=hexDarkGrey, fg="white",
                            font=("Arial", 13))
        other_label.place(anchor="center", relx=0.5, rely=0.55)

        # # Stockpile connection label
        stockpile_connection_label = Label(self.sideFrame,
                                           text="Connecté au "
                                                "stockage :",
                                           bg=hexDarkGrey, fg="white",
                                           font=("Arial", 10))
        stockpile_connection_label.place(anchor="center", relx=0.5,
                                         rely=0.65)

        # # Stockpile connection boolean label
        self.stockpile_boolean_label = Label(self.sideFrame,
                                             text="Oui",
                                             bg=hexDarkGrey, fg="white",
                                             font=("Arial", 10))
        self.stockpile_boolean_label.place(anchor="center", relx=0.5,
                                           rely=0.72)


class BuildingWindow(Frame):
    name_label: Label
    level_label: Label
    upgrade_canvas: Canvas

    def __init__(self, master):
        super().__init__(master)
        # self.building_info = building_info
        self.create_layout()
        self.bind_on_click()
        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=75, height=75)

    def create_layout(self):
        """Crée le layout du bâtiment window"""
        self.name_label = Label(self, text="Batiment", bg=hexDark,
                                fg="white", font=("Arial", 10))
        self.name_label.place(anchor="center", relx=0.45, rely=0.2)

        self.level_label = Label(self, text="Tier 1", bg=hexDark,
                                 fg="white", font=("Arial", 10))
        self.level_label.place(anchor="center", relx=0.7, rely=0.8)

        self.upgrade_canvas = Canvas(self, bg=hexDark, width=20, height=20,
                                     bd=0, highlightthickness=0)
        self.upgrade_canvas.place(anchor="center", relx=0.2, rely=0.8)

        # make an upward pointing arrow

        self.upgrade_canvas.create_polygon(10, 0, 0, 20, 20, 20, fill="white")

    def bind_on_click(self):
        for widget in self.winfo_children():
            widget.bind("<Button-1>", self.on_window_click)
        self.bind("<Button-1>", self.on_window_click)

        self.upgrade_canvas.bind("<Button-1>", self.on_upgrade_click)

    def on_window_click(self, _):
        print("Window clicked")

    def on_upgrade_click(self, _):
        print("Upgrade clicked")


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.geometry("400x400")
    PlanetWindow(root).pack()
    root.mainloop()
