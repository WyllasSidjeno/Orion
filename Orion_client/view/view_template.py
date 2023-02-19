from __future__ import annotations
import random
from tkinter import Frame, Label, Canvas, Scrollbar
from typing import Any

from Orion_client.model.model import Model

hexDarkGrey = "#36393f"
hexDark = "#2f3136"
hexSpaceBlack = "#23272a"


class PlanetWindow(Frame):
    # todo : Make sure GameCanvas is appropriate
    def __init__(self, parent: GameCanvas):
        """Initialise la fenetre"""
        super().__init__(parent, bg=hexDarkGrey, bd=1, relief="solid",
                         width=400, height=400)

        # # # Le Header
        self.header_frame: Frame = Frame(self, bg=hexDarkGrey,
                                         bd=1, relief="solid")
        """Frame contenant les informations identifiantes de la planete"""

        self.owner_label = Label(self.header_frame, bg=hexDarkGrey,
                                 fg="white", font=("Arial", 15))
        """Label contenant le nom du proprietaire de la planete"""

        self.population_canvas = Canvas(self.header_frame, bg=hexDarkGrey,
                                        width=51, height=51,
                                        highlightthickness=0)
        """Canvas contenant le label de la population"""
        self.population_canvas.create_oval(0, 0, 50, 50, fill="dark green")
        """Cercle de la population"""
        self.population_label = Label(self.population_canvas,
                                      bg="dark green", fg="white",
                                      font=("Arial", 8))
        """Label contenant la population"""

        self.name_label = Label(self.header_frame,
                                bg=hexDarkGrey, fg="white",
                                font=("Arial", 20))
        """Label contenant le nom de la planete"""

        # # # La main frame
        self.main_frame: Frame = Frame(self, bg=hexDarkGrey, bd=1,
                                       relief="solid")
        """Frame contenant les batiments de la planete"""
        self.building_label = Label(self.main_frame, text="Batiments",
                                    bg=hexDarkGrey, fg="white",
                                    font=("Arial", 13))
        """Label contenant le nom du header du menu de batiment"""

        self.building_grid = Frame(self.main_frame, bg=hexDarkGrey)
        """Frame contenant les batiments de la planete"""

        # # # Side Frame
        self.side_frame = Frame(self, bg=hexDarkGrey, bd=1, relief="solid")
        """Frame contenant les informations de production de la planete"""

        self.ressource_label = Label(self.side_frame, text="Ressources",
                                     bg=hexDarkGrey, fg="white",
                                     font=("Arial", 13))
        """Label contenant le nom du header du menu de ressource"""

        self.line = Frame(self.side_frame, bg="white", bd=1, relief="solid")

        self.other_label = Label(self.side_frame, text="Autre",
                                 bg=hexDarkGrey, fg="white",
                                 font=("Arial", 13))
        """Label contenant le nom du header du menu d'information"""

        self.stockpile_connection_label = Label(self.side_frame,
                                                text="Connecté au "
                                                     "stockage :",
                                                bg=hexDarkGrey, fg="white",
                                                font=("Arial", 10))
        """Label contenant le nom du header du menu d'information"""
        self.stockpile_boolean_label = Label(self.side_frame,
                                             text="Oui",
                                             bg=hexDarkGrey, fg="white",
                                             font=("Arial", 10))
        """Label contenant le nom du header du menu d'information"""

        self.configure_placement()

    def show(self, planet_info: dict) -> None:
        """Affiche les informations de la planete

        :param planet_info: Dictionnaire contenant les informations de la
        planete"""
        # todo : Make sure it works with all ressources once implemented
        self.owner_label.config(text=planet_info["owner"])
        self.population_label.config(text=planet_info["population"])
        self.name_label.config(text=planet_info["name"])

        # Make it so it doesnt make the window bigger and that it gets over
        # the current content of the window
        self.lift()

    def hide(self) -> None:
        """Cache la fenetre"""
        self.lower()

    def configure_placement(self) -> None:
        """Place les widgets dans la fenetre"""
        self.place_header()
        self.place_main()
        self.place_side_bar()
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.lower()

    def place_header(self) -> None:
        """Crée le header de la fenetre, la ou les informations identifiante
        de la planete sont affichées
        """
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        self.owner_label.place(anchor="center", relx=0.12, rely=0.2)

        self.population_canvas.place(anchor="center", relx=0.85, rely=0.45)
        self.population_label.place(anchor="center", relx=0.5, rely=0.5)

        self.name_label.place(anchor="center", relx=0.1, rely=0.7)

    def place_main(self) -> None:
        """Crée le main de la fenetre, là ou les bâtiments sont affichés

        :param planet_info: Dictionnaire contenant"""
        # Start with the main frame
        self.main_frame.place(relx=0, rely=0.2, relwidth=0.60, relheight=0.8)

        self.building_label.place(anchor="center", relx=0.5, rely=0.05)

        # # Building grid

        self.building_grid.place(relx=0.1, rely=0.1, relwidth=0.8,
                                 relheight=0.9)

        # # Building frames (depending on the number of buildings)
        # for i, building in enumerate(planet_info):
        # setattr(self, f"{building}_frame",
        # BuildingWindow(building_grid))
        # if i % 2 == 0:  # If the building is on the left
        # getattr(self,
        # f'{building}_frame').grid(row=i // 2, column=0,
        #   padx=10, pady=10)
        # else:  # If the building is on the right
        # getattr(self,
        # f'{building}_frame').grid(row=i // 2, column=1,
        #                          padx=10, pady=10)

    def place_side_bar(self) -> None:
        """Crée le side de la fenetre, là oú le rendement de la planete est
        affiché"""
        self.side_frame.place(relx=0.60, rely=0.2, relwidth=0.40,
                              relheight=0.8)

        self.ressource_label.place(anchor="center", relx=0.5, rely=0.05)

        # # Ressource labels
        # for i, ressource in enumerate(planet_info):
        #    setattr(self, f"{ressource}_label",
        #            Label(self.side_frame,
        #                  text=ressource + " : " + str(planet_info[ressource]),
        #                  bg=hexDarkGrey, fg="white", font=("Arial", 10)))
        #
        #           getattr(self, f"{ressource}_label").place(anchor="center",
        # relx=0.5,
        # rely=0.13 + i * 0.1)

        self.line.place(relx=0.1, rely=0.5, relwidth=0.8, relheight=0.01)

        self.other_label.place(anchor="center", relx=0.5, rely=0.55)

        self.stockpile_connection_label.place(anchor="center", relx=0.5,
                                              rely=0.65)

        self.stockpile_boolean_label.place(anchor="center", relx=0.5,
                                           rely=0.72)


class BuildingWindow(Frame):
    name_label: Label
    level_label: Label
    upgrade_canvas: Canvas

    def __init__(self, master: Frame, building_info: dict):
        """Crée la fenetre d'un bâtiment

        :param master: Frame parent
        :param building_info: Dictionnaire contenant les informations du
        bâtiment"""
        super().__init__(master)

        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=75, height=75)

        self.name_label = Label(self, text="Batiment", bg=hexDark,
                                fg="white", font=("Arial", 10))
        """Label contenant le nom du bâtiment"""

        self.level_label = Label(self, text="Tier 1", bg=hexDark,
                                 fg="white", font=("Arial", 10))
        """Label contenant le niveau du bâtiment"""

        self.upgrade_canvas = Canvas(self, bg=hexDark, width=20, height=20,
                                     bd=0, highlightthickness=0)
        """Canvas contenant le bouton d'amélioration du bâtiment"""

        self.upgrade_canvas.create_polygon(10, 0, 0, 20, 20, 20, fill="white")
        """Triangle blanc représentant le bouton d'amélioration"""

        self.configure_placement()

        self.bind_on_click()

    def configure_placement(self):
        """Crée le layout du bâtiment window"""
        # todo : self place les widgets ?

        self.name_label.place(anchor="center", relx=0.45, rely=0.2)

        self.level_label.place(anchor="center", relx=0.7, rely=0.8)

        self.upgrade_canvas.place(anchor="center", relx=0.2, rely=0.8)

    def bind_on_click(self):
        """Bind les fonctions de click sur les widgets"""
        for widget in self.winfo_children():
            widget.bind("<Button-1>", self.on_window_click)
        self.bind("<Button-1>", self.on_window_click)

        self.upgrade_canvas.bind("<Button-1>", self.on_upgrade_click)

    def on_window_click(self, _):
        """ Fonction appelée quand on clique sur la fenetre du bâtiment"""
        print("Window clicked")

    def on_upgrade_click(self, _):
        """ Fonction appelée quand on clique sur le bouton d'amélioration"""
        print("Upgrade clicked")


class GameCanvas(Canvas):
    """ Représente le canvas de jeu, ce qui veux dire l'ensemble des
    planetes, vaisseaux spaciaux et autres objets du jeu qui ne sont
    pas des menus ou des fenetres ou de l'information
    """

    # todo : Make the tags more streamlined and documented.
    def __init__(self, master: Frame, scroll_x: Scrollbar,
                 scroll_y: Scrollbar):
        """Initialise le canvas de jeu
        :param master: Le Frame parent
        :param scroll_x: La scrollbar horizontale
        :param scroll_y: La scrollbar verticale
        """
        super().__init__(master)
        self.configure(bg=hexSpaceBlack, bd=1,
                       relief="solid", highlightthickness=0,
                       xscrollcommand=scroll_x.set,
                       yscrollcommand=scroll_y.set)

        scroll_x.config(command=self.xview)
        scroll_y.config(command=self.yview)

        self.configure(scrollregion=(0, 0, 9000, 9000))

    def initialize(self, mod):
        """Initialise le canvas de jeu avec les données du model
        lors de sa création
        :param mod: Le model"""
        self.generate_background(mod.largeur, mod.hauteur,
                                 len(mod.etoiles) * 50)
        self.generate_unowned_stars(mod.etoiles)
        owned_stars = self.get_player_stars(mod)
        self.generate_owned_stars(owned_stars)
        self.generate_wormhole(mod.trou_de_vers)

    @staticmethod
    def get_player_stars(mod):
        """Récupère les étoiles contrôlées par le joueur
        :param mod: Le model
        :return: Une liste d'étoiles"""
        stars = []
        for star in mod.joueurs.keys():
            for j in mod.joueurs[star].etoilescontrolees:
                j.col = "blue"  # mod.joueurs[star].couleur
                stars.append(j)
        return stars

    def generate_background(self, width, height, n):
        """ Genère un background de n étoiles de tailles aléatoires
        :param width: La largeur du background
        :param height: La hauteur du background
        :param n: Le nombre d'étoiles à générer"""
        for i in range(n):
            x, y = random.randrange(int(width)), random.randrange(int(height))
            size = random.randrange(3) + 1
            col = random.choice(["lightYellow", "lightBlue", "lightGreen"])

            self.create_oval(x - size, y - size, x + size, y + size,
                             fill=col, tags="background")

    def generate_unowned_stars(self, stars):
        """Créé les étoiles qui n'appartienne à personne sur le canvas."""
        for star in stars:
            self.generate_star(star, "stars_unowned")

    def generate_owned_stars(self, stars):
        """Créé les étoiles qui appartiennent á un joueur sur le canvas."""
        for star in stars:
            self.generate_star(star, "stars_owned")

    def generate_star(self, star, tag: str):
        """Créé une étoile sur le canvas.
        :param star: L'étoile à créer
        :param tag: Un tag de l'étoile"""
        size = star.taille * 2  # Legacy JM
        self.create_oval(star.x - size, star.y - size,
                         star.x + size, star.y + size,
                         fill="grey",
                         tags=(tag, star.id, star.proprietaire))

    def generate_wormhole(self, wormholes):
        """Créé deux portes de trou de vers sur le canvas. """

        for wormhole in wormholes:
            self.generate_wormdoor(wormhole.porte_a, wormhole.id)
            self.generate_wormdoor(wormhole.porte_b, wormhole.id)

    def generate_wormdoor(self, door, parent_id: str):
        """Créé une porte de trou de vers sur le canvas."""
        self.create_oval(door.x - door.pulse, door.y - door.pulse,
                         door.x + door.pulse, door.y + door.pulse,
                         fill=door.couleur,
                         tags=("Wormhole", door.id, parent_id))

    def horizontal_scroll(self, event):
        """Effectue un scroll horizontal sur le canvas."""
        self.xview_scroll(-1 * int(event.delta / 120), "units")

    def vertical_scroll(self, event):
        """Effectue un scroll vertical sur le canvas."""
        self.yview_scroll(-1 * int(event.delta / 120), "units")

    def refresh(self, mod):
        """Rafrachit le canvas de jeu avec les données du model
        :param mod: Le model"""
        # todo : Optimize the movement so we do not have to
        #  delete but only move it with move()

        self.delete("stars_owned")
        self.delete("Wormhole")
        self.delete("spaceship")

        owned_stars = self.get_player_stars(mod)
        self.generate_owned_stars(owned_stars)
        self.generate_wormhole(mod.trou_de_vers)


class Minimap(Canvas):
    """ Représente la minimap du jeu."""
    def __init__(self, master: Frame):
        """Initialise la minimap"""
        super().__init__(master)
        self.configure(bg=hexDark, bd=1,
                       relief="solid", highlightthickness=1)

        self.bind("<Button-1>", self.on_click)  # todo : Move to controller

    def on_click(self, event) -> tuple[int, int]:
        """Récupère les coordonnées de la minimap lors d'un clic
        :param event: L'événement du clic
        :return: Les coordonnées du clic relative au canvas de jeu"""
        y_factor = 9000 / self.winfo_height()  # todo : Send from model
        x_factor = 9000 / self.winfo_width()  # todo : Send from model

        repx = event.x * x_factor
        repy = event.y * y_factor
        print(
            f"Minimap clicked at {event.x}, {event.y} - {repx}, {repy}")

        return int(repx), int(repy)

    def initialize(self, mod):
        """Initialise la minimap avec les données du model
        lors de sa création
        :param mod: Le model"""
        pass
        # todo : Generate the minimap and integrate
        #  the .place() method here instead
