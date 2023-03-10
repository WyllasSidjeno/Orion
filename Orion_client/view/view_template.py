from __future__ import annotations
import random
from functools import partial
from tkinter import Frame, Label, Canvas, Scrollbar, Button, Menu
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Orion_client.model.modele import Modele
    from Orion_client.model.space_object import TrouDeVers, PorteDeVers

from Orion_client.helper import LogHelper

hexDarkGrey: str = "#36393f"
"""Couleur de fond des frames"""
hexDark: str = "#2f3136"
"""Couleur de fond de l'application"""
hexSpaceBlack: str = "#23272a"
"""Pour l'espace, on utilise un noir plus sombre"""


class EtoileWindow(Frame):
    planet_id: int
    def __init__(self, parent: GameCanvas):
        """Initialise la fenetre"""
        super().__init__(parent, bg=hexDarkGrey, bd=1, relief="solid",
                         width=500, height=500)

        self.log: LogHelper = LogHelper()

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
                                                text="Connect?? au "
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
        self.construct_ship_menu = ConstructShipMenu(self.side_frame)
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

    def get_all_view_logs(self) -> list[str]:
        """Retourne tous les logs de la fenetre"""
        for i in self.construct_ship_menu.log.get_and_clear():
            self.log.add_log(i)
        return self.log.get_and_clear()

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
        """Cr??e le header de la fenetre, la ou les informations identifiante
        de la planete sont affich??es
        """
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        self.proprietaire_label.place(anchor="center", relx=0.12, rely=0.2)

        self.population_canvas.place(anchor="center", relx=0.85, rely=0.45)
        self.population_label.place(anchor="center", relx=0.5, rely=0.5)

        self.nom_label.place(anchor="center", relx=0.1, rely=0.7)

    def place_main(self) -> None:
        """Cr??e le main de la fenetre, l?? ou les b??timents sont affich??s
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
        """Cr??e le side de la fenetre, l?? o?? le rendement de la planete est
        affich??"""
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
        """Affiche les b??timents de la planete"""
        for i in range(max_building):
            self.building_list[i].show(row=i // 3, column=i % 3, padx=5,
                                       pady=5)


class BuildingWindow(Frame):
    name_label: Label
    level_label: Label
    upgrade_canvas: Canvas

    def __init__(self, master: Frame):
        """Cr??e la fenetre d'un b??timent
        :param master: Frame parent
        """
        super().__init__(master)

        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=75, height=75)

        self.name_label = Label(self, text="Batiment", bg=hexDark,
                                fg="white", font=("Arial", 10))
        """Label contenant le nom du b??timent"""

        self.level_label = Label(self, text="Tier 1", bg=hexDark,
                                 fg="white", font=("Arial", 10))
        """Label contenant le niveau du b??timent"""

        self.upgrade_canvas = Canvas(self, bg=hexDark, width=20, height=20,
                                     bd=0, highlightthickness=0)
        """Canvas contenant le bouton d'am??lioration du b??timent"""

        self.upgrade_canvas.create_polygon(10, 0, 0, 20, 20, 20, fill="white")
        """Triangle blanc repr??sentant le bouton d'am??lioration"""

    def initialize(self):
        """Cr??e le layout du b??timent window"""
        # todo : self place les widgets ?

        self.name_label.place(anchor="center", relx=0.45, rely=0.2)

        self.level_label.place(anchor="center", relx=0.7, rely=0.8)

        self.upgrade_canvas.place(anchor="center", relx=0.2, rely=0.8)

    def hide(self):
        self.grid_forget()

    def show(self, **kwargs):
        self.grid(**kwargs)


class GameCanvas(Canvas):
    """ Repr??sente le canvas de jeu, ce qui veux dire l'ensemble des
    planetes, vaisseaux spaciaux et autres objets du jeu qui ne sont
    pas des menus ou des fenetres ou de l'information
    """

    # todo : Make the tags more streamlined and documented.
    username: str

    def __init__(self, master: Frame, scroll_x: Scrollbar,
                 scroll_y: Scrollbar):
        """Initialise le canvas de jeu
        :param master: Le Frame parent
        :param scroll_x: La scrollbar horizontale
        :param scroll_y: La scrollbar verticale
        """
        super().__init__(master)
        self.log = LogHelper()
        self.configure(bg=hexSpaceBlack, bd=1,
                       relief="solid", highlightthickness=0,
                       xscrollcommand=scroll_x.set,
                       yscrollcommand=scroll_y.set)

        scroll_x.config(command=self.xview)
        scroll_y.config(command=self.yview)

        self.configure(scrollregion=(0, 0, 9000, 9000))
        self.ship_view = ShipViewGenerator()

        self.planet_window = EtoileWindow(self)
        """Repr??sente la fen??tre de plan??te de la vue du jeu."""
        self.planet_window.hide()

    def move_to(self, x: float, y: float) -> None:
        """D??place le canvas de jeu ?? une position donn??e
        :param x: La position x en 0.0 - 1.0
        :param y: La position y en 0.0 - 1.0
        """
        self.xview_moveto(x)
        self.yview_moveto(y)

    def initialize(self, mod: Modele):
        """Initialise le canvas de jeu avec les donn??es du model
        lors de sa cr??ation
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
        """R??cup??re les ??toiles contr??l??es par le joueur
        :param mod: Le model
        :return: Une liste d'??toiles"""
        stars = []
        for star in mod.joueurs.keys():
            for j in mod.joueurs[star].etoiles_controlees:
                stars.append(j)
        return stars

    def generate_background(self, width: int, height: int, n: int):
        """ Gen??re un background de n ??toiles de tailles al??atoires
        :param width: La largeur du background
        :param height: La hauteur du background
        :param n: Le nombre d'??toiles ?? g??n??rer"""
        for i in range(n):
            x, y = random.randrange(int(width)), random.randrange(int(height))
            size = random.randrange(3) + 1
            col = random.choice(["lightYellow", "lightBlue", "lightGreen"])

            self.create_oval(x - size, y - size, x + size, y + size,
                             fill=col, tags="background")

    def generate_etoile(self, star, tag: str):
        """Cr???? une ??toile sur le canvas.
        :param star: L'??toile ?? cr??er
        :param tag: Un tag de l'??toile"""
        size = star.taille * 2  # Legacy JM
        self.create_oval(star.x - size, star.y - size,
                         star.x + size, star.y + size,
                         fill="grey",
                         tags=(tag, star.id, star.proprietaire))

    def generate_trou_de_vers(self, trou_de_vers : list[TrouDeVers]):
        """Cr???? deux portes de trou de vers sur le canvas. """

        for wormhole in trou_de_vers:
            self.generate_porte_de_vers(wormhole.porte_a, wormhole.id)
            self.generate_porte_de_vers(wormhole.porte_b, wormhole.id)

    def generate_porte_de_vers(self, porte: PorteDeVers, parent_id: str):
        """Cr???? une porte de trou de vers sur le canvas."""
        self.create_oval(porte.x - porte.pulse, porte.y - porte.pulse,
                         porte.x + porte.pulse, porte.y + porte.pulse,
                         fill=porte.couleur,
                         tags=("TrouDeVers", porte.id, parent_id))

    def refresh(self, mod: Modele):
        """Rafrachit le canvas de jeu avec les donn??es du model
        :param mod: Le model"""
        # todo : Optimize the movement so we do not have to
        #  delete but only move it with a move or coords function

        self.delete("TrouDeVers")
        self.delete("etoile_occupee")

        owned_stars = self.get_player_stars(mod)
        for i in range(len(owned_stars)):
            self.generate_etoile(owned_stars[i], "etoile_occupee")

        self.generate_trou_de_vers(mod.trou_de_vers)  # TODO : To fix

        for joueur in mod.joueurs.keys():
            for armada in mod.joueurs[joueur].flotte.keys():
                if mod.joueurs[joueur].flotte[armada].nouveau:
                    self.ship_view. \
                        generate_ship_view(self,
                                           mod.joueurs[joueur].flotte[
                                               armada].position,
                                           mod.joueurs[joueur].couleur,
                                           mod.joueurs[joueur].flotte[
                                               armada].id,
                                           mod.joueurs[joueur].flotte[
                                               armada].owner,
                                           mod.joueurs[joueur].flotte[
                                               armada].__repr__()
                                           )
                    mod.joueurs[joueur].flotte[armada].nouveau = False
                elif mod.joueurs[joueur].flotte[
                    armada].position_cible is not None:
                    self.ship_view.move(self, mod.joueurs[joueur].flotte[
                        armada].position, mod.joueurs[joueur].flotte[
                                            armada].id,
                                        mod.joueurs[joueur].flotte[
                                            armada].__repr__())

        self.tag_raise("vaisseau")

    def get_all_view_logs(self) -> list[str]:
        """R??cup??re tous les logs du canvas de jeu."""
        for i in self.planet_window.get_all_view_logs():
            self.log.add_log(i)

        return self.log.get_and_clear()

    def horizontal_scroll(self, event):
        """Effectue un scroll horizontal sur le canvas."""
        self.xview_scroll(-1 * int(event.delta / 120), "units")

    def vertical_scroll(self, event):
        """Effectue un scroll vertical sur le canvas."""
        self.yview_scroll(-1 * int(event.delta / 120), "units")


class SideBar(Frame):
    """ Repr??sente la sidebar du jeu."""

    def __init__(self, master: Frame):
        """Initialise la sidebar"""
        super().__init__(master)
        self.log = LogHelper()
        self.configure(bg=hexDark, bd=1,
                       relief="solid")

        self.planet_frame = Frame(self, bg=hexDark, bd=1,
                                  relief="solid")

        self.planet_label = Label(self.planet_frame, text="Planet",
                                  bg=hexDark, fg="white",
                                  font=("Arial", 20))

        self.armada_frame = Frame(self, bg=hexDark, bd=1,
                                  relief="solid")
        """Repr??sente le cadre de la vue du jeu contenant les informations"""
        self.armada_label = Label(self.armada_frame, text="Armada",
                                  bg=hexDark, fg="white",
                                  font=("Arial", 20))
        """Repr??sente le label de la vue du jeu contenant les informations"""

        self.minimap_frame = Frame(self, bg=hexDark, bd=1,
                                   relief="solid")
        """Repr??sente le cadre de la vue du jeu contenant les informations"""
        self.minimap_label = Label(self.minimap_frame, text="Minimap",
                                   bg=hexDark, fg="white",
                                   font=("Arial", 20))
        """Repr??sente le label de la vue du jeu contenant les informations"""
        self.minimap = Minimap(self.minimap_frame)
        """Repr??sente le lbel de la vue du jeu contenant les informations"""

        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        # Make sure they all stay the same size 1/3

    def initialize(self, mod):
        """Initialise la sidebar avec les donn??es du model
        lors de sa cr??ation
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
        self.minimap_frame.grid_columnconfigure(0, weight=1)
        self.minimap_frame.grid_rowconfigure(1, weight=6)

        self.minimap_label.grid(row=0, column=0, sticky="nsew")
        self.minimap.grid(row=1, column=0, sticky="nsew")

        self.minimap.initialize(mod)

    def refresh(self, mod):
        """Rafraichit la sidebar avec les donn??es du model
        lors de sa cr??ation
        :param mod: Le model"""
        self.minimap.refresh(mod)


class Minimap(Canvas):
    """ Repr??sente la minimap du jeu."""
    x_ratio: float
    y_ratio: float

    def __init__(self, master: Frame):
        """Initialise la minimap"""
        super().__init__(master, bg=hexDark, bd=1,
                         relief="solid", highlightthickness=0)

        # Make it the same size as the master
        self.propagate(False)

    def initialize(self, mod: Modele):
        """Initialise la minimap avec les donn??es du model"""
        self.update_idletasks()

        self.x_ratio = self.winfo_width() / mod.largeur
        self.y_ratio = self.winfo_height() / mod.hauteur

        for star in mod.etoiles:
            self.create_oval(star.x * self.x_ratio - 2,
                             star.y * self.y_ratio - 2,
                             star.x * self.x_ratio + 2,
                             star.y * self.y_ratio + 2,
                             fill="grey", tags="etoile")

        for key in mod.joueurs:
            for star in mod.joueurs[key].etoiles_controlees:
                self.create_oval(star.x * self.x_ratio - 2,
                                 star.y * self.y_ratio - 2,
                                 star.x * self.x_ratio + 2,
                                 star.y * self.y_ratio + 2,
                                 fill="white", tags="etoile_controlee")

        for wormhole in mod.trou_de_vers:
            self.create_oval(wormhole.porte_a.x * self.x_ratio - 2,
                             wormhole.porte_a.y * self.y_ratio - 2,
                             wormhole.porte_a.x * self.x_ratio + 2,
                             wormhole.porte_a.y * self.y_ratio + 2,
                             fill=wormhole.porte_a.couleur, tags="TrouDeVers")
            self.create_oval(wormhole.porte_b.x * self.x_ratio - 2,
                             wormhole.porte_b.y * self.y_ratio - 2,
                             wormhole.porte_b.x * self.x_ratio + 2,
                             wormhole.porte_b.y * self.y_ratio + 2,
                             fill=wormhole.porte_b.couleur, tags="TrouDeVers")

            self.bind("<Configure>", self.on_resize)

    def refresh(self, mod: Modele):
        """Rafraichit la minimap avec les donn??es du model"""
        pass
        # todo : Refresh only what necessary or the whole thing ?

    def on_resize(self, _):
        """G??re le redimensionnement de la minimap"""
        self.update_idletasks()

        old_ratio_x = self.x_ratio
        old_ratio_y = self.y_ratio

        self.x_ratio = self.winfo_width() / 9000
        self.y_ratio = self.winfo_height() / 9000

        diff_ratio_x = self.x_ratio / old_ratio_x
        diff_ratio_y = self.y_ratio / old_ratio_y

        for star in self.find_withtag("etoile"):
            self.coords(star, self.coords(star)[0] * diff_ratio_x,
                        self.coords(star)[1] * diff_ratio_y,
                        self.coords(star)[2] * diff_ratio_x,
                        self.coords(star)[3] * diff_ratio_y)

        for star in self.find_withtag("etoile_controlee"):
            self.coords(star, self.coords(star)[0] * diff_ratio_x,
                        self.coords(star)[1] * diff_ratio_y,
                        self.coords(star)[2] * diff_ratio_x,
                        self.coords(star)[3] * diff_ratio_y)

        for wormhole in self.find_withtag("TrouDeVers"):
            self.coords(wormhole, self.coords(wormhole)[0] * diff_ratio_x,
                        self.coords(wormhole)[1] * diff_ratio_y,
                        self.coords(wormhole)[2] * diff_ratio_x,
                        self.coords(wormhole)[3] * diff_ratio_y)


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
            "Transport": {
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
        canvas.coords(ship_id, pos[0] - self.settings["Reconnaissance"]["size"],
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
                      pos[0] - self.settings["Transport"]["size"],
                      pos[1] - self.settings["Transport"]["size"],
                      pos[0] + self.settings["Transport"]["size"],
                      pos[1] + self.settings["Transport"]["size"])

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
        """Creer un arc dans le canvas ?? la position donn??e tout en
        utilisant les param??tres du vaisseau"""
        master.create_arc(pos[0] - self.settings["Reconnaissance"]["size"],
                          pos[1] - self.settings["Reconnaissance"]["size"],
                          pos[0] + self.settings["Reconnaissance"]["size"],
                          pos[1] + self.settings["Reconnaissance"]["size"],
                          start=0, extent=180, fill=couleur,
                          tags=("vaisseau", ship_id, username, ship_type))

    def create_transportation(self, master: Canvas, pos: tuple, couleur: str,
                     ship_id: str, username: str, ship_type: str):
        """Creer un rectangle dans le canvas ?? la position donn??e tout en
        utilisant les param??tres du vaisseau"""
        master.create_rectangle(pos[0] - self.settings["Transport"]["size"],
                                pos[1] - self.settings["Transport"]["size"],
                                pos[0] + self.settings["Transport"]["size"],
                                pos[1] + self.settings["Transport"]["size"],
                                fill=couleur,
                                tags=("vaisseau", ship_id, username, ship_type))

    def create_militaire(self, master: Canvas, pos: tuple, couleur: str,
                       ship_id: str, username: str, ship_type: str):
        """Creer un triangle dans le canvas ?? la position donn??e tout en
        utilisant les param??tres du vaisseau"""

        master.create_polygon(pos[0],
                              pos[1] - self.settings["Militaire"]["size"],
                              pos[0] - self.settings["Militaire"]["size"],
                              pos[1] + self.settings["Militaire"]["size"],
                              pos[0] + self.settings["Militaire"]["size"],
                              pos[1] + self.settings["Militaire"]["size"],
                              fill=couleur,
                              tags=("vaisseau", ship_id, username, ship_type))


class ConstructShipMenu(Menu):
    """Menu deroulant qui affiche la possibilite des constructions de vaisseaux
    """
    planet_id: str

    def __init__(self, master: Frame):
        """Initialise le menu deroulant"""
        super().__init__(master, tearoff=0, bg=hexDarkGrey)
        self.log = LogHelper()
        self.ship_types = ["Reconnaissance", "Militaire", "Transport"]

        for i in range(len(self.ship_types)):
            self.add_command(label=self.ship_types[i],
                             command=partial(self.add_event_to_log, i))

    def add_event_to_log(self, i):
        """Ajoute un evenement de construction de vaisseau au log"""
        self.log.add("main_player", "construct_ship", self.planet_id,
                     self.ship_types[i].lower())

    def hide(self, _):
        """Cache le menu"""
        self.unpost()

    def show(self, event, planet_id):
        """Montre le menu a la position de la souris"""
        self.planet_id = planet_id
        self.post(event.x_root, event.y_root)
