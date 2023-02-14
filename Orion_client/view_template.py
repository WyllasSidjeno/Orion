from tkinter import Frame, Label
from typing import Any

hexColor = "#36393f"


class PlanetWindow(Frame):
    """Fenetre qui affiche les informations d'une planete"""
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
                "Metal": 0,
                "Beton": 0,
                "Energie": 0,
                "Nourriture": 0
            },
            "building": {
                "b1",
                "b2",
                "b3",
                "b4",
            }
        }

        self.headerFrame: Frame = \
            Frame(self, bg=hexColor, bd=1, relief="solid")
        self.mainFrame: Frame = Frame(self, bg=hexColor, bd=1,
                                      relief="solid")
        self.sideFrame = Frame(self, bg=hexColor, bd=1, relief="solid")

        self.create_layout(self.planetInfo)

    def create_layout(self, planetInfo) -> None:
        """Crée le layout de la fenetre, c'est à dire les frames et les
        widgets"""
        self.configure(bg="dark grey", width=400, height=400)

        self.create_header(planetInfo["header"])
        self.create_main(planetInfo["building"])
        self.create_side(planetInfo["output"])

    def create_header(self, planet_info) -> None:
        """Crée le header de la fenetre, la ou les informations identifiante
        de la planete sont affichées

        :param planet_info: Dictionnaire contenant
        les informations de la planete
        """
        self.headerFrame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        name_label = Label(self.headerFrame, text=planet_info["name"],
                           bg=hexColor, fg="white", font=("Arial", 15))
        name_label.place(anchor="center", relx=0.1, rely=0.2)

        population_label = Label(self.headerFrame,
                                 text=planet_info["population"],
                                 bg=hexColor, fg="white",
                                 font=("Arial", 10))
        population_label.place(anchor="center", relx=0.9, rely=0.2)

        owner_label = Label(self.headerFrame, text=planet_info["owner"],
                            bg=hexColor, fg="white", font=("Arial", 20))
        owner_label.place(anchor="center", relx=0.5, rely=0.7)

    def create_main(self, planet_info) -> None:
        """Crée le main de la fenetre, là ou les bâtiments sont affichés

        :param planet_info: Dictionnaire contenant"""
        self.mainFrame.place(relx=0, rely=0.2, relwidth=0.60, relheight=0.8)

        building_label = Label(self.mainFrame, text="Batiments",
                               bg=hexColor, fg="white",
                               font=("Arial", 13))
        building_label.place(anchor="center", relx=0.5, rely=0.05)

        building_grid = Frame(self.mainFrame, bg=hexColor)
        building_grid.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.9)

        for i, building in enumerate(planet_info):
            building_frame = Frame(building_grid, bg="white", bd=1,
                                   relief="solid", width=75, height=75)
            if i % 2 == 0:
                building_frame.grid(row=i // 2, column=0, padx=10, pady=10)
            else:
                building_frame.grid(row=i // 2, column=1, padx=10, pady=10)

    def create_side(self, planet_info) -> None:
        """Crée le side de la fenetre, là oú le rendement de la planete est
        affiché"""
        self.sideFrame.place(relx=0.60, rely=0.2, relwidth=0.40, relheight=0.8)

        ressource_label = Label(self.sideFrame, text="Ressources",
                                bg=hexColor, fg="white",
                                font=("Arial", 13))
        ressource_label.place(anchor="center", relx=0.5, rely=0.05)

        for i, ressource in enumerate(planet_info):
            ressource_label = Label(self.sideFrame,
                                    text=ressource + " : " +
                                         str(planet_info[ressource]),
                                    bg=hexColor, fg="white",
                                    font=("Arial", 10))
            ressource_label.place(anchor="center", relx=0.5,
                                  rely=0.13 + i * 0.1)

        line = Frame(self.sideFrame, bg="white", bd=1, relief="solid")
        line.place(relx=0.1, rely=0.5, relwidth=0.8, relheight=0.01)

        other_label = Label(self.sideFrame, text="Autre",
                            bg=hexColor, fg="white",
                            font=("Arial", 13))
        other_label.place(anchor="center", relx=0.5, rely=0.55)

        stockpile_connection_label = Label(self.sideFrame,
                                           text="Connecté au "
                                                "stockage :",
                                           bg=hexColor, fg="white",
                                           font=("Arial", 10))
        stockpile_connection_label.place(anchor="center", relx=0.5,
                                         rely=0.65)
        stockpile_boolean_label = Label(self.sideFrame,
                                        text="Oui",
                                        bg=hexColor, fg="white",
                                        font=("Arial", 10))
        stockpile_boolean_label.place(anchor="center", relx=0.5,
                                      rely=0.72)


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.geometry("400x400")
    PlanetWindow(root).pack()
    root.mainloop()
