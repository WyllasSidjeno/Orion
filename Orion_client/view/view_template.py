from __future__ import annotations
import random
from functools import partial
from tkinter import Frame, Label, Canvas, Scrollbar, Button, Menu
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Orion_client.model.modele import Modele
    from Orion_client.model.space_object import TrouDeVers, PorteDeVers

hexDarkGrey: str = "#36393f"
"""Couleur de fond des frames"""
hexDark: str = "#2f3136"
"""Couleur de fond de l'application"""
hexSpaceBlack: str = "#23272a"
"""Pour l'espace, on utilise un noir plus sombre"""


class EtoileWindow(Frame):
    planet_id: int

    def __init__(self, parent: GameCanvas, command_queue):
        """Initialise la fenetre"""
        super().__init__(parent, bg=hexDarkGrey, bd=1, relief="solid",
                         width=500, height=500)

        self.command_queue = command_queue

        self.is_shown: bool = False
        """Si la fenetre est affichee"""

        # # # Le Header
        self.header_frame: Frame = Frame(self, bg=hexDarkGrey,
                                         bd=1, relief="solid")
        """Frame contenant les informations identifiantes de la planete"""

        self.proprietaire_label = Label(self.header_frame, bg=hexDarkGrey,
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

        self.nom_label = Label(self.header_frame,
                               bg=hexDarkGrey, fg="white",
                               font=("Arial", 20))
        """Label contenant le nom de la planete"""

        # # # La main frame
        self.main_frame: Frame = Frame(self, bg=hexDarkGrey, bd=1,
                                       relief="solid")
        """Frame contenant les batiments de la planete"""
        self.batiment_label = Label(self.main_frame, text="Batiments",
                                    bg=hexDarkGrey, fg="white",
                                    font=("Arial", 13))
        """Label contenant le nom du header du menu de batiment"""

        self.batiment_grid = Frame(self.main_frame, bg=hexDarkGrey)
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
                                             text="",
                                             bg=hexDarkGrey, fg="white",
                                             font=("Arial", 10))
        """Label contenant le nom du header du menu d'information"""

        self.construct_ship_button = Button(self.side_frame,
                                            text="Construire un vaisseau",
                                            bg=hexDarkGrey, fg="white",
                                            font=("Arial", 10))
        self.construct_ship_menu = ConstructShipMenu(self.side_frame,
                                                     self.command_queue)
        x, y = self.construct_ship_button.winfo_rootx(), \
            self.construct_ship_button.winfo_rooty()

        self.construct_ship_button.bind("<Button-1>",
                                        self.show_construct_menu)
        self.bind("<Button-1>", self.construct_ship_menu.hide)

        self.building_list = []

        for i in range(8):
            self.building_list.append(BuildingWindow(self.batiment_grid))

    def show_construct_menu(self, event) -> None:
        """Affiche le menu de construction de vaisseau"""
        self.construct_ship_menu.show(event, self.planet_id)

    def hide(self) -> None:
        """Cache la fenetre"""
        self.construct_ship_menu.current_planet_id = None
        self.place_forget()
        self.is_shown = False

    def show(self, planet_id: int) -> None:
        """Affiche la fenetre"""
        self.planet_id = planet_id
        self.construct_ship_menu.current_planet_id = planet_id
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.is_shown = True

    def initialize(self) -> None:
        """Place les widgets dans la fenetre"""
        self.place_header()
        self.place_main()
        self.place_side_bar()
        for i in self.building_list:
            i.initialize()

    def place_header(self) -> None:
        """Crée le header de la fenetre, la ou les informations identifiante
        de la planete sont affichées
        """
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        self.proprietaire_label.place(anchor="center", relx=0.12, rely=0.2)

        self.population_canvas.place(anchor="center", relx=0.85, rely=0.45)
        self.population_label.place(anchor="center", relx=0.5, rely=0.5)

        self.nom_label.place(anchor="center", relx=0.1, rely=0.7)

    def place_main(self) -> None:
        """Crée le main de la fenetre, là ou les bâtiments sont affichés
        """
        # Start with the main frame
        self.main_frame.place(relx=0, rely=0.2, relwidth=0.60, relheight=0.8)

        self.batiment_label.place(anchor="center", relx=0.5, rely=0.05)

        # # Building grid

        self.batiment_grid.place(relx=0.1, rely=0.1, relwidth=0.8,
                                 relheight=0.9)

        self.batiment_grid.columnconfigure(0, weight=1)
        self.batiment_grid.columnconfigure(1, weight=1)
        self.batiment_grid.columnconfigure(2, weight=1)

        self.batiment_grid.rowconfigure(0, weight=1)
        self.batiment_grid.rowconfigure(1, weight=1)
        self.batiment_grid.rowconfigure(2, weight=1)

    def place_side_bar(self) -> None:
        """Crée le side de la fenetre, là oú le rendement de la planete est
        affiché"""
        self.side_frame.place(relx=0.60, rely=0.2, relwidth=0.40,
                              relheight=0.8)

        self.ressource_label.place(anchor="center", relx=0.5, rely=0.05)

        # # Ressource labels

        self.line.place(relx=0.1, rely=0.5, relwidth=0.8, relheight=0.01)

        self.other_label.place(anchor="center", relx=0.5, rely=0.55)

        self.stockpile_connection_label.place(anchor="center", relx=0.5,
                                              rely=0.65)

        self.stockpile_boolean_label.place(anchor="center", relx=0.5,
                                           rely=0.72)

        self.construct_ship_button.place(anchor="center", relx=0.5,
                                         rely=0.85)

    def show_buildings(self, max_building: int) -> None:
        """Affiche les bâtiments de la planete"""
        for i in range(max_building):
            self.building_list[i].show(row=i // 3, column=i % 3, padx=5,
                                       pady=5)


class BuildingWindow(Frame):
    name_label: Label
    level_label: Label
    upgrade_canvas: Canvas

    def __init__(self, master: Frame):
        """Crée la fenetre d'un bâtiment
        :param master: Frame parent
        """
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

    def initialize(self):
        """Crée le layout du bâtiment window"""
        # todo : self place les widgets ?

        self.name_label.place(anchor="center", relx=0.45, rely=0.2)

        self.level_label.place(anchor="center", relx=0.7, rely=0.8)

        self.upgrade_canvas.place(anchor="center", relx=0.2, rely=0.8)

    def hide(self):
        self.grid_forget()

    def show(self, **kwargs):
        self.grid(**kwargs)


class GameCanvas(Canvas):
    """ Représente le canvas de jeu, ce qui veux dire l'ensemble des
    planetes, vaisseaux spaciaux et autres objets du jeu qui ne sont
    pas des menus ou des fenetres ou de l'information
    """

    # todo : Make the tags more streamlined and documented.
    username: str

    def __init__(self, master: Frame, scroll_x: Scrollbar,
                 scroll_y: Scrollbar, command_queue):
        """Initialise le canvas de jeu
        :param master: Le Frame parent
        :param scroll_x: La scrollbar horizontale
        :param scroll_y: La scrollbar verticale
        """
        super().__init__(master)
        self.command_queue = command_queue
        self.configure(bg=hexSpaceBlack, bd=1,
                       relief="solid", highlightthickness=0,
                       xscrollcommand=scroll_x.set,
                       yscrollcommand=scroll_y.set)

        scroll_x.config(command=self.xview)
        scroll_y.config(command=self.yview)

        self.configure(scrollregion=(0, 0, 9000, 9000))
        self.ship_view = ShipViewGenerator()

        self.planet_window = EtoileWindow(self, self.command_queue)
        """Représente la fenêtre de planète de la vue du jeu."""
        self.planet_window.hide()

    def move_to(self, x: float, y: float) -> None:
        """Déplace le canvas de jeu à une position donnée
        :param x: La position x en 0.0 - 1.0
        :param y: La position y en 0.0 - 1.0
        """
        self.xview_moveto(x)
        self.yview_moveto(y)

    def initialize(self, mod: Modele):
        """Initialise le canvas de jeu avec les données du model
        lors de sa création
        :param mod: Le model"""
        # mod mandatory because of background dependancy
        self.generate_background(mod.largeur, mod.hauteur,
                                 len(mod.etoiles) * 50)
        for i in range(len(mod.etoiles)):
            self.generate_etoile(mod.etoiles[i], "unowned_star")

        owned_stars = self.get_player_stars(mod)
        # todo : Colors
        for i in range(len(owned_stars)):
            self.generate_etoile(owned_stars[i], "owned_star")
        self.generate_trou_de_vers(mod.trou_de_vers)

    @staticmethod
    def get_player_stars(mod: Modele):
        """Récupère les étoiles contrôlées par le joueur
        :param mod: Le model
        :return: Une liste d'étoiles"""
        stars = []
        for star in mod.joueurs.keys():
            for j in mod.joueurs[star].etoiles_controlees:
                stars.append(j)
        return stars

    def generate_background(self, width: int, height: int, n: int):
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

    def generate_etoile(self, star, tag: str, *args):
        """Créé une étoile sur le canvas.
        :param star: L'étoile à créer
        :param tag: Un tag de l'étoile"""
        size = star.taille * 2  # Legacy JM
        self.create_oval(star.x - size, star.y - size,
                         star.x + size, star.y + size,
                         fill=star.couleur,
                         tags=(tag, star.id, star.proprietaire))

    def generate_trou_de_vers(self, trou_de_vers: list[TrouDeVers]):
        """Créé deux portes de trou de vers sur le canvas. """

        for wormhole in trou_de_vers:
            self.generate_porte_de_vers(wormhole.porte_a, wormhole.id)
            self.generate_porte_de_vers(wormhole.porte_b, wormhole.id)

    def generate_porte_de_vers(self, porte: PorteDeVers, parent_id: str):
        """Créé une porte de trou de vers sur le canvas."""
        self.create_oval(porte.x - porte.pulse, porte.y - porte.pulse,
                         porte.x + porte.pulse, porte.y + porte.pulse,
                         fill="purple",
                         tags=("TrouDeVers", porte.id, parent_id))

    def refresh(self, mod: Modele):
        """Rafrachit le canvas de jeu avec les données du model
        :param mod: Le model"""
        # todo : Optimize the movement so we do not have to
        #  delete but only move it with a move or coords function

        self.delete("TrouDeVers")
        self.delete("etoile_occupee")

        owned_stars = self.get_player_stars(mod)
        for i in range(len(owned_stars)):
            self.generate_etoile(owned_stars[i], "etoile_occupee", )

        self.generate_trou_de_vers(mod.trou_de_vers)  # TODO : To fix

        for joueur in mod.joueurs.values():
            couleur = joueur.couleur
            for ship_type in joueur.flotte.keys():
                for ship_id in joueur.flotte[ship_type]:
                    ship = joueur.flotte[ship_type][ship_id]
                    if ship.nouveau:
                        self.ship_view.generate_ship_view(self, ship.position,
                                                          couleur,
                                                          ship.id,
                                                          joueur.nom,
                                                          ship_type)
                        ship.nouveau = False

                    else:
                        self.ship_view.move(self, ship.position, ship.id,
                                            ship_type)

        self.tag_raise("vaisseau")

    def horizontal_scroll(self, event):
        """Effectue un scroll horizontal sur le canvas."""
        self.xview_scroll(-1 * int(event.delta / 120), "units")

    def vertical_scroll(self, event):
        """Effectue un scroll vertical sur le canvas."""
        self.yview_scroll(-1 * int(event.delta / 120), "units")


class SideBar(Frame):
    """ Représente la sidebar du jeu."""

    def __init__(self, master: Frame, command_queue):
        """Initialise la sidebar"""
        super().__init__(master)
        self.command_queue = command_queue
        self.configure(bg=hexDark, bd=1,
                       relief="solid")

        self.planet_frame = Frame(self, bg=hexDark, bd=1,
                                  relief="solid")

        self.planet_label = Label(self.planet_frame, text="Planet",
                                  bg=hexDark, fg="white",
                                  font=("Arial", 20))

        self.armada_frame = Frame(self, bg=hexDark, bd=1,
                                  relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.armada_label = Label(self.armada_frame, text="Armada",
                                  bg=hexDark, fg="white",
                                  font=("Arial", 20))
        """Représente le label de la vue du jeu contenant les informations"""

        self.minimap_frame = Frame(self, bg=hexDark, bd=1,
                                   relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.minimap_label = Label(self.minimap_frame, text="Minimap",
                                   bg=hexDark, fg="white",
                                   font=("Arial", 20))
        """Représente le label de la vue du jeu contenant les informations"""
        self.minimap = Minimap(self.minimap_frame)
        """Représente le lbel de la vue du jeu contenant les informations"""

        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        # Make sure they all stay the same size 1/3

    def initialize(self, mod):
        """Initialise la sidebar avec les données du model
        lors de sa création
        :param mod: Le model"""

        self.planet_frame.grid(row=0, column=0, sticky="nsew")
        self.planet_frame.grid_propagate(False)
        self.armada_frame.grid(row=1, column=0, sticky="nsew")
        self.armada_frame.grid_propagate(False)
        self.minimap_frame.grid(row=2, column=0, sticky="nsew")
        self.minimap_frame.grid_propagate(False)

        self.planet_frame.grid_rowconfigure(0, weight=1)
        self.planet_frame.grid_columnconfigure(0, weight=1)
        self.planet_frame.grid_rowconfigure(1, weight=6)

        self.planet_label.grid(row=0, column=0, sticky="nsew")

        self.armada_frame.grid_rowconfigure(0, weight=1)
        self.armada_frame.grid_columnconfigure(0, weight=1)
        self.armada_frame.grid_rowconfigure(1, weight=6)

        self.armada_label.grid(row=0, column=0, sticky="nsew")

        self.minimap_frame.grid_rowconfigure(0, weight=1)
        self.minimap_frame.grid_rowconfigure(1, weight=3)
        self.minimap_frame.grid_rowconfigure(2, weight=1)

        self.minimap_frame.grid_columnconfigure(0, weight=1)
        self.minimap_frame.grid_columnconfigure(1, weight=2)
        self.minimap_frame.grid_columnconfigure(2, weight=1)

        self.minimap_frame.grid_propagate(False)

        self.minimap_label.grid(row=0, column=1, sticky="nsew")
        self.minimap.grid(row=1, column=1, sticky="nsew")
        self.minimap_frame.grid_propagate(False)

        self.minimap.initialize(mod)

    def refresh(self, mod):
        """Rafraichit la sidebar avec les données du model
        lors de sa création
        :param mod: Le model"""
        self.minimap.refresh(mod)


class Minimap(Canvas):
    """ Représente la minimap du jeu."""
    x_ratio: float
    y_ratio: float
    old_x_ratio: float
    old_y_ratio: float

    def __init__(self, master: Frame):
        """Initialise la minimap"""
        super().__init__(master, bg=hexDark, bd=1,
                         relief="solid", highlightthickness=0)

        self.propagate(False)

    def initialize(self, mod: Modele):
        """Initialise la minimap avec les données du model"""
        self.update_idletasks()
        size = min(self.winfo_width(), self.winfo_height())
        self.config(width=size, height=size)

        self.x_ratio = self.winfo_width() / mod.largeur
        self.y_ratio = self.winfo_height() / mod.hauteur

        for star in mod.etoiles:
            self.create_oval(star.x * self.x_ratio - 2,
                             star.y * self.y_ratio - 2,
                             star.x * self.x_ratio + 2,
                             star.y * self.y_ratio + 2,
                             fill="grey", tags="etoile"
                             , outline=hexSpaceBlack)

        for key in mod.joueurs:
            for star in mod.joueurs[key].etoiles_controlees:
                print(star.x, star.y, star.id)
                self.create_oval(star.x * self.x_ratio - 2,
                                 star.y * self.y_ratio - 2,
                                 star.x * self.x_ratio + 2,
                                 star.y * self.y_ratio + 2,
                                 fill=mod.joueurs[key].couleur,
                                 tags="etoile_controlee",
                                 outline=hexSpaceBlack)

        for wormhole in mod.trou_de_vers:
            self.create_oval(wormhole.porte_a.x * self.x_ratio - 2,
                             wormhole.porte_a.y * self.y_ratio - 2,
                             wormhole.porte_a.x * self.x_ratio + 2,
                             wormhole.porte_a.y * self.y_ratio + 2,
                             fill="purple", tags="TrouDeVers"
                             , outline=hexSpaceBlack)
            self.create_oval(wormhole.porte_b.x * self.x_ratio - 2,
                             wormhole.porte_b.y * self.y_ratio - 2,
                             wormhole.porte_b.x * self.x_ratio + 2,
                             wormhole.porte_b.y * self.y_ratio + 2,
                             fill="purple", tags="TrouDeVers",
                             outline=hexSpaceBlack)

            self.bind("<Configure>", self.on_resize)

    def refresh(self, mod: Modele):
        """Rafraichit la minimap avec les données du model"""
        pass
        # todo : Refresh only what necessary or the whole thing ?

    def on_resize(self, _):
        """Gère le redimensionnement de la minimap"""
        print("resize")
        width = self.winfo_width()
        height = self.winfo_height()

        self.old_x_ratio = self.x_ratio
        self.old_y_ratio = self.y_ratio

        self.x_ratio = width / 9000
        self.y_ratio = height / 9000

        for star in self.find_withtag("etoile"):
            x1, y1, x2, y2 = self.coords(star)
            new_x1 = x1 * self.x_ratio / self.old_x_ratio
            new_y1 = y1 * self.y_ratio / self.old_y_ratio
            new_x2 = x2 * self.x_ratio / self.old_x_ratio
            new_y2 = y2 * self.y_ratio / self.old_y_ratio
            self.delete(star)
            self.create_oval(new_x1, new_y1, new_x2, new_y2,
                             fill="grey", tags="etoile",
                             outline=hexSpaceBlack)

        for star in self.find_withtag("etoile_controlee"):
            x1, y1, x2, y2 = self.coords(star)
            color = self.itemcget(star, "fill")
            new_x1 = x1 * self.x_ratio / self.old_x_ratio
            new_y1 = y1 * self.y_ratio / self.old_y_ratio
            new_x2 = x2 * self.x_ratio / self.old_x_ratio
            new_y2 = y2 * self.y_ratio / self.old_y_ratio
            self.delete(star)
            self.create_oval(new_x1, new_y1, new_x2, new_y2,
                             fill=color, tags="etoile_controlee",
                             outline=hexSpaceBlack)

        for wormhole in self.find_withtag("TrouDeVers"):
            x1, y1, x2, y2 = self.coords(wormhole)
            new_x1 = x1 * self.x_ratio / self.old_x_ratio
            new_y1 = y1 * self.y_ratio / self.old_y_ratio
            new_x2 = x2 * self.x_ratio / self.old_x_ratio
            new_y2 = y2 * self.y_ratio / self.old_y_ratio
            self.delete(wormhole)
            self.create_oval(new_x1, new_y1, new_x2, new_y2,
                             fill="purple", tags="TrouDeVers",
                             outline=hexSpaceBlack)

        self.old_x_ratio = self.x_ratio
        self.old_y_ratio = self.y_ratio


class ShipViewGenerator:
    """Class that generates all ships view.
    This includes Reconnaissance, Militaire and Transportation."""

    def __init__(self):
        self.settings = {
            "Reconnaissance": {
                "size": 7,
            },
            "Militaire": {
                "size": 10,
            },
            "Transportation": {
                "size": 12
            }
        }

    def move(self, canvas, pos, ship_tag, ship_type):
        """Move the ship to the given position"""
        if ship_type == "reconnaissance":
            self.move_reconnaissance(canvas, ship_tag, pos)
        elif ship_type == "militaire":
            self.move_militaire(canvas, ship_tag, pos)
        elif ship_type == "transportation":
            self.move_transportation(canvas, ship_tag, pos)

    def move_reconnaissance(self, canvas, ship_tag, pos):
        """Move the recon to the given position"""
        # get the ship id using the ship tag
        ship_id = canvas.find_withtag(ship_tag)[0]
        canvas.coords(ship_id,
                      pos[0] - self.settings["Reconnaissance"]["size"],
                      pos[1] - self.settings["Reconnaissance"]["size"],
                      pos[0] + self.settings["Reconnaissance"]["size"],
                      pos[1] + self.settings["Reconnaissance"]["size"])

    def move_militaire(self, canvas, ship_tag, pos):
        """Move the fighter to the given position"""
        ship_id = canvas.find_withtag(ship_tag)[0]
        canvas.coords(ship_id, pos[0],
                      pos[1] - self.settings["Militaire"]["size"],
                      pos[0] - self.settings["Militaire"]["size"],
                      pos[1] + self.settings["Militaire"]["size"],
                      pos[0] + self.settings["Militaire"]["size"],
                      pos[1] + self.settings["Militaire"]["size"])

    def move_transportation(self, canvas, ship_tag, pos):
        """Move the cargo to the given position"""
        ship_id = canvas.find_withtag(ship_tag)[0]
        # Move a polygon
        canvas.coords(ship_id,
                      pos[0] - self.settings["Transportation"]["size"],
                      pos[1] - self.settings["Transportation"]["size"],
                      pos[0] + self.settings["Transportation"]["size"],
                      pos[1] + self.settings["Transportation"]["size"])

    @staticmethod
    def delete(canvas: Canvas, ship_id: str):
        """Delete the ship from the canvas"""
        canvas.delete(ship_id)

    def generate_ship_view(self, master: Canvas, pos: tuple, couleur: str,
                           ship_id: str, username: str, ship_type: str):
        """Generate a ship view depending on the type of ship"""
        if ship_type == "reconnaissance":
            self.create_reconnaissance(master, pos, couleur, ship_id, username,
                                       ship_type)
        elif ship_type == "militaire":
            self.create_militaire(master, pos, couleur, ship_id, username,
                                  ship_type)
        elif ship_type == "transportation":
            self.create_transportation(master, pos, couleur, ship_id, username,
                                       ship_type)

    def create_reconnaissance(self, master: Canvas, pos: tuple, couleur: str,
                              ship_id: str, username: str, ship_type: str):
        """Creer un arc dans le canvas à la position donnée tout en
        utilisant les paramètres du vaisseau"""
        master.create_arc(pos[0] - self.settings["Reconnaissance"]["size"],
                          pos[1] - self.settings["Reconnaissance"]["size"],
                          pos[0] + self.settings["Reconnaissance"]["size"],
                          pos[1] + self.settings["Reconnaissance"]["size"],
                          start=0, extent=180, fill=couleur,
                          tags=("vaisseau", ship_id, username, ship_type),
                          outline=hexSpaceBlack)

    def create_transportation(self, master: Canvas, pos: tuple, couleur: str,
                              ship_id: str, username: str, ship_type: str):
        """Creer un rectangle dans le canvas à la position donnée tout en
        utilisant les paramètres du vaisseau"""
        master.create_rectangle(
            pos[0] - self.settings["Transportation"]["size"],
            pos[1] - self.settings["Transportation"]["size"],
            pos[0] + self.settings["Transportation"]["size"],
            pos[1] + self.settings["Transportation"]["size"],
            fill=couleur,
            tags=("vaisseau", ship_id, username, ship_type),
            outline=hexSpaceBlack)

    def create_militaire(self, master: Canvas, pos: tuple, couleur: str,
                         ship_id: str, username: str, ship_type: str):
        """Creer un triangle dans le canvas à la position donnée tout en
        utilisant les paramètres du vaisseau"""

        master.create_polygon(pos[0],
                              pos[1] - self.settings["Militaire"]["size"],
                              pos[0] - self.settings["Militaire"]["size"],
                              pos[1] + self.settings["Militaire"]["size"],
                              pos[0] + self.settings["Militaire"]["size"],
                              pos[1] + self.settings["Militaire"]["size"],
                              fill=couleur,
                              tags=("vaisseau", ship_id, username, ship_type),
                              outline=hexSpaceBlack)


class ConstructShipMenu(Menu):
    """Menu deroulant qui affiche la possibilite des constructions de vaisseaux
    """
    planet_id: str

    def __init__(self, master: Frame, command_queue):
        """Initialise le menu deroulant"""
        super().__init__(master, tearoff=0, bg=hexDarkGrey)
        self.command_queue = command_queue
        self.ship_types = ["Reconnaissance", "Militaire", "Transportation"]

        for i in range(len(self.ship_types)):
            self.add_command(label=self.ship_types[i],
                             command=partial(self.add_event_to_command_queue,
                                             i))

    def add_event_to_command_queue(self, i):
        """Ajoute un evenement de construction de vaisseau au command_queue"""
        self.command_queue.add("main_player", "construct_ship_request",
                               self.planet_id, self.ship_types[i].lower())

    def hide(self, _):
        """Cache le menu"""
        self.unpost()

    def show(self, event, planet_id):
        """Montre le menu a la position de la souris"""
        self.planet_id = planet_id
        self.post(event.x_root, event.y_root)
