from functools import partial
from tkinter import Frame, Label, Canvas, Button, Menu

from Orion_client.helpers.CommandQueues import ControllerQueue, JoueurQueue
from Orion_client.helpers.helper import StringTypes
from Orion_client.view.view_common_ressources import *


class EtoileWindow(Frame):
    star_id: int | None

    def __init__(self, master, proprietaire: str):
        """Initialise la fenetre"""
        super().__init__(master, bg=hexDarkGrey, bd=1, relief="solid",
                         width=500, height=500)

        self.is_shown: bool = False
        """Si la fenetre est affichee"""

        # # # Le Header
        self.header_frame: Frame = Frame(self, bg=hexDarkGrey,
                                         bd=1, relief="solid")
        """Frame contenant les informations identifiantes de la planete"""

        self.proprietaire_label = Label(self.header_frame, bg=hexDarkGrey,
                                        fg="white", font=("Arial", 15))
        """Label contenant le nom du proprietaire de la planete"""
        self.proprietaire_label["text"] = proprietaire

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
        self.batiment_label = Label(self.main_frame, text="Colonies",
                                    bg=hexDarkGrey, fg="white",
                                    font=("Arial", 13))
        """Label contenant le nom du header du menu de batiment"""

        self.batiment_grid = Frame(self.main_frame, bg=hexDarkGrey)
        """Frame contenant les batiments de la planete"""

        # # # Side Frame
        self.side_frame = Frame(self, bg=hexDarkGrey, bd=1, relief="solid")
        """Frame contenant les informations de production de la planete"""

        self.ressource_grid = Frame(self.side_frame, bg=hexDarkGrey)
        """Frame contenant les ressources de la planete"""

        self.ressource_label = Label(self.side_frame, text="Rendement :",
                                     bg=hexDarkGrey, fg="white",
                                     font=("Arial", 13))
        """Label contenant le nom du header du menu de ressource"""

        self.energie_label = Label(self.ressource_grid, text="energie :",
                                   bg=hexDarkGrey, fg="white",
                                   font=("Arial", 10))
        self.energie_value_label = Label(self.ressource_grid, text="0",
                                         bg=hexDarkGrey, fg="white",
                                         font=("Arial", 10))

        self.metal_label = Label(self.ressource_grid, text="Métal :",
                                 bg=hexDarkGrey, fg="white",
                                 font=("Arial", 10))
        self.metal_value_label = Label(self.ressource_grid, text="0",
                                       bg=hexDarkGrey, fg="white",
                                       font=("Arial", 10))

        self.beton_label = Label(self.ressource_grid, text="Béton :",
                                 bg=hexDarkGrey, fg="white",
                                 font=("Arial", 10))
        self.beton_value_label = Label(self.ressource_grid, text="0",
                                       bg=hexDarkGrey, fg="white",
                                       font=("Arial", 10))

        self.nourriture_label = Label(self.ressource_grid, text="Nourriture :",
                                      bg=hexDarkGrey, fg="white",
                                      font=("Arial", 10))
        self.nourriture_value_label = Label(self.ressource_grid, text="0",
                                            bg=hexDarkGrey, fg="white",
                                            font=("Arial", 10))

        self.science_label = Label(self.ressource_grid, text="Science :",
                                   bg=hexDarkGrey, fg="white",
                                   font=("Arial", 10))
        self.science_value_label = Label(self.ressource_grid, text="0",
                                         bg=hexDarkGrey, fg="white",
                                         font=("Arial", 10))

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
                                             text="Non",
                                             bg=hexDarkGrey, fg="white",
                                             font=("Arial", 10))
        """Label contenant le nom du header du menu d'information"""

        self.construct_ship_button = Button(self.side_frame,
                                            text="Construire un vaisseau",
                                            bg=hexDarkGrey, fg="white",
                                            font=("Arial", 10))
        self.construct_ship_menu = ConstructShipMenu(self.side_frame)

        self.construct_ship_button.bind("<Button-1>",
                                        self.show_construct_ship_menu)

        self.building_list = []

        self.construct_building_menu = ConstructBuildingMenu(self.side_frame)

        for i in range(8):
            self.building_list.append(BuildingWindow(self.batiment_grid))

        self.place_header()
        self.place_main()
        self.place_side_bar()

        self.header_frame.bind("<Button-1>", self.start_move)
        self.header_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.header_frame.bind("<B1-Motion>", self.do_move)

    def start_move(self, _) -> None:
        """Démarre le déplacement de la fenetre
        """
        self.x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        self.y = self.master.winfo_pointery() - self.master.winfo_rooty()

    def stop_move(self, _) -> None:
        """Arrête le déplacement de la fenetre
        """
        self.x = None
        self.y = None

    def do_move(self, _) -> None:
        """Déplace la fenetre en suivant la souris
        """
        if self.x is not None and self.y is not None:
            x = self.master.winfo_pointerx() - self.x - self.master.winfo_rootx()
            y = self.master.winfo_pointery() - self.y - self.master.winfo_rooty()
            self.place(x=x, y=y)

    def place_header(self) -> None:
        """Crée le header de la fenetre, la ou les informations identifiante
        de la planete sont affichées
        """
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        self.proprietaire_label.place(anchor="center", relx=0.12, rely=0.2)

        self.population_canvas.place(anchor="center", relx=0.85, rely=0.45)
        self.population_label.place(anchor="center", relx=0.5, rely=0.5)

        self.nom_label.place(anchor="w", relx=0.02, rely=0.7)

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

        self.ressource_grid.place(relx=0.1, rely=0.1,
                                  relwidth=0.8, relheight=0.4)
        self.ressource_grid.columnconfigure(0, weight=1)
        self.ressource_grid.columnconfigure(1, weight=1)
        self.ressource_grid.rowconfigure(0, weight=1)
        self.ressource_grid.rowconfigure(1, weight=1)
        self.ressource_grid.rowconfigure(2, weight=1)
        self.ressource_grid.rowconfigure(3, weight=1)
        self.ressource_grid.rowconfigure(4, weight=1)

        self.energie_label.grid(row=0, column=0, sticky="nsew")
        self.energie_value_label.grid(row=0, column=1, sticky="nsew")

        self.metal_label.grid(row=1, column=0, sticky="nsew")
        self.metal_value_label.grid(row=1, column=1, sticky="nsew")

        self.nourriture_label.grid(row=2, column=0, sticky="nsew")
        self.nourriture_value_label.grid(row=2, column=1, sticky="nsew")

        self.science_label.grid(row=3, column=0, sticky="nsew")
        self.science_value_label.grid(row=3, column=1, sticky="nsew")

        self.beton_label.grid(row=4, column=0, sticky="nsew")
        self.beton_value_label.grid(row=4, column=1, sticky="nsew")

        self.line.place(relx=0.1, rely=0.55, relwidth=0.8, relheight=0.01)

        self.other_label.place(anchor="center", relx=0.5, rely=0.6)

        self.stockpile_connection_label.place(anchor="center", relx=0.5,
                                              rely=0.70)

        self.stockpile_boolean_label.place(anchor="center", relx=0.5,
                                           rely=0.77)

        self.construct_ship_button.place(anchor="center", relx=0.5,
                                         rely=0.9)

    def refresh(self, model):
        """Rafraichit la fenetre"""
        star = model.get_object(self.star_id, StringTypes.ETOILE_OCCUPEE)
        self.population_label.config(text=star.population)
        self.stockpile_boolean_label.config(
            text="Oui" if star.transit else "Non")

        max_building = star.buildinglist.__len__()

        for i in range(star.taille):
            self.building_list[i].show(row=i // 3, column=i % 3)
            self.building_list[i].reinitialize()
            if i < max_building:
                self.building_list[i].show_building(star.buildinglist[i])

            else:
                self.building_list[i].bind("<Button-1>",
                                           lambda event, i=i:
                                           self.construct_building_menu.show(
                                               event, i))

        output = star.output.__dict__()
        self.energie_value_label.config(text=output["energie"])
        self.metal_value_label.config(text=output["metal"])
        self.beton_value_label.config(text=output["beton"])
        self.nourriture_value_label.config(text=output["nourriture"])
        self.science_value_label.config(text=output["science"])

        self.nom_label.config(text=star.name)

    def hide(self) -> None:
        """Cache la fenetre"""
        self.place_forget()
        for i in range(8):
            if self.building_list[i].is_shown:
                self.building_list[i].hide()
        self.is_shown = False
        self.construct_ship_menu.current_star_id = None
        self.star_id = None

    def show(self, star_id: int) -> None:
        """Affiche la fenetre"""
        self.star_id = star_id
        self.construct_ship_menu.current_planet_id = star_id
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.is_shown = True

    def show_construct_ship_menu(self, event) -> None:
        """Affiche le menu de construction de vaisseau"""
        self.construct_ship_menu.show(event, self.star_id)

    def show_buildings(self, max_building: int) -> None:
        """Affiche les bâtiments de la planete"""
        for i in range(max_building):
            self.building_list[i].show(row=i // 3, column=i % 3, padx=5,
                                       pady=5)


class BuildingWindow(Frame):
    name_label: Label
    level_label: Label
    upgrade_canvas: Canvas

    def __init__(self, master):
        """Crée la fenetre d'un bâtiment
        """
        super().__init__(master)

        self.config(bg=hexDark, bd=2,
                    relief="solid",
                    width=75, height=75)

        self.name_label = Label(self, text="Libre", bg=hexDark,
                                fg="white", font=("Arial", 10))
        """Label contenant le nom du bâtiment"""

        self.level_label = Label(self, text="", bg=hexDark,
                                 fg="white", font=("Arial", 10))
        """Label contenant le niveau du bâtiment"""

        self.upgrade_canvas = Canvas(self, bg=hexDark, width=20, height=20,
                                     bd=0, highlightthickness=0)
        """Canvas contenant le bouton d'amélioration du bâtiment"""

        self.name_label.place(anchor="center", relx=0.45, rely=0.2)

        self.level_label.place(anchor="center", relx=0.7, rely=0.8)

        self.upgrade_canvas.place(anchor="center", relx=0.2, rely=0.8)

        self.is_shown = False

    def hide(self):
        self.grid_forget()
        self.is_shown = False

    def show(self, **kwargs):
        self.grid(**kwargs)
        self.is_shown = True

    def reinitialize(self):
        self.name_label.config(text="Libre")
        self.level_label.config(text="")
        self.upgrade_canvas.delete("all")

    def show_building(self, building):
        self.name_label.config(text=building.name)
        self.level_label.config(text=building.level)
        self.upgrade_canvas.create_polygon(10, 0, 0, 20, 20, 20, fill="white")


class ConstructShipMenu(Menu):
    """Menu deroulant qui affiche la possibilite des constructions de vaisseaux
    """
    planet_id: str
    command_queue: ControllerQueue

    def __init__(self, master: Frame):
        """Initialise le menu deroulant"""
        super().__init__(master, tearoff=0, bg=hexDarkGrey)
        self.ship_types = ["Reconnaissance", "Militaire", "Transportation"]

        for i in range(len(self.ship_types)):
            self.add_command(label=self.ship_types[i],
                             command=partial(self.add_event_to_command_queue,
                                             i))

    def register_command_queue(self, command_queue: ControllerQueue):
        """Enregistre la file de commandes"""
        self.command_queue = command_queue

    def add_event_to_command_queue(self, i):
        """Ajoute un evenement de construction de vaisseau au
        view_controller_queue"""
        self.command_queue. \
            handle_ship_construct_request(self.planet_id,
                                          self.ship_types[i].lower())

    def hide(self, _):
        """Cache le menu"""
        self.unpost()

    def show(self, event, planet_id):
        """Montre le menu a la position de la souris"""
        self.planet_id = planet_id
        self.post(event.x_root, event.y_root)


class ConstructBuildingMenu(Menu):
    planet_id: str
    command_queue: ControllerQueue

    def __init__(self, master: Frame):
        """Initialise le menu deroulant"""
        super().__init__(master, tearoff=0, bg=hexDarkGrey)
        self.building_types = ["Mine", "Farm", "Concrete Factory",
                               "Power Plant", "Research Center"]

        self.add_command(label="Annuler", command=self.hide)
        self.add_separator()
        for i in range(len(self.building_types)):
            self.add_command(label=self.building_types[i])
            self.entryconfig(i + 2, command=partial(self.on_click, i))

    def hide(self):
        """Cache le menu"""
        self.unpost()

    def show(self, event, planet_id):
        """Montre le menu a la position de la souris"""
        self.planet_id = planet_id
        self.post(event.x_root, event.y_root)

    def on_click(self, i):
        type = self.building_types[i].lower().replace(" ", "")
        self.command_queue.handle_building_construct_request(self.planet_id,
                                                             type)
        self.hide()

    def register_command_queue(self, command_queue: ControllerQueue):
        """Enregistre la file de commandes"""
        self.command_queue = command_queue
