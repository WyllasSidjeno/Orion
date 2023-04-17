from __future__ import annotations
import random
import tkinter
from tkinter import Frame, Label, Canvas, Scrollbar, Text, END, Entry, Tk
from PIL import Image
from typing import TYPE_CHECKING

from PIL import ImageTk

from Orion_client.helpers.CommandQueues import ControllerQueue
from Orion_client.helpers.helper import StringTypes

from Orion_client.view.view_common_ressources import *
from Orion_client.view.star_template import EtoileWindow

if TYPE_CHECKING:
    from Orion_client.model.modele import Modele
    from Orion_client.model.space_object import TrouDeVers, PorteDeVers

hexDarkGrey: str = "#36393f"
"""Couleur de fond des frames"""
hexDark: str = "#2f3136"
"""Couleur de fond de l'application"""
hexSpaceBlack: str = "#23272a"
"""Pour l'espace, on utilise un noir plus sombre"""

class GameCanvas(Canvas):
    """ Représente le canvas de jeu, ce qui veux dire l'ensemble des
    planetes, vaisseaux spaciaux et autres objets du jeu qui ne sont
    pas des menus ou des fenetres ou de l'information
    """
    username: str
    command_queue: ControllerQueue

    def __init__(self, master, scroll_x: Scrollbar,
                 scroll_y: Scrollbar, proprietaire):
        """Initialise le canvas de jeu
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
        self.generate_background(9000)

        self.ship_view = ShipViewGenerator()

        self.etoile_window = EtoileWindow(master, proprietaire)
        """Représente la fenêtre de planète de la vue du jeu."""
        self.etoile_window.hide()

        self.photo_cache = {
            "white": Image.open("assets/planet/star_white01.png"),
            "blue": Image.open("assets/planet/star_blue01.png"),
            "red": Image.open("assets/planet/star_red01.png"),
            "yellow": Image.open("assets/planet/star_yellow01.png"),
            "orange": Image.open("assets/planet/star_orange01.png"),
        }

        self.cache = []

        self.mouseOverView = MouseOverView(self)

        self.tag_bind(StringTypes.ETOILE.value, "<Enter>",
                      self.mouse_over_view_show)

    def mouse_over_view_show(self, event):
        self.mouseOverView = MouseOverView(self)
        self.mouseOverView.show(event)
        self.tag_bind(StringTypes.ETOILE.value, "<Leave>",
                      self.mouseOverView.hide)

    def refresh(self, mod: Modele):
        """Rafrachit le canvas de jeu avec les données du model
        :param mod: Le model"""
        # todo : Optimize the movement so we do not have to
        #  delete but only move it with a move or coords function
        if self.etoile_window.star_id is not None:
            self.etoile_window.refresh(mod)
        self.delete(StringTypes.TROUDEVERS.value)

        if self.mouseOverView.visible:
            item_tags = self.gettags("current")
            obj = mod.get_object(item_tags[1], item_tags[0])
            self.mouseOverView.on_mouse_over(obj.to_mouse_over_dict())

        stars = mod.get_player_stars() + mod.etoiles

        for star in stars:
            if star.id not in self.cache or star.needs_refresh:
                if star.needs_refresh:
                    self.delete(star.id)
                if star.proprietaire != '':
                    tags = StringTypes.ETOILE_OCCUPEE.value
                else:
                    tags = StringTypes.ETOILE.value
                self.generate_etoile(star, tags)
                self.cache.append(star.id)

        self.generate_trou_de_vers(mod.trou_de_vers)

        # todo : Could be optimized.
        for joueur in mod.joueurs.values():
            if joueur.recently_lost_ships_id:
                for ship_id in joueur.recently_lost_ships_id:
                    self.delete(ship_id)
                joueur.recently_lost_ships_id = []

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

    def move_to(self, x: float, y: float) -> None:
        """Déplace le canvas de jeu à une position donnée
        :param x: La position x en 0.0 - 1.0
        :param y: La position y en 0.0 - 1.0
        """

        """ Bouge le canvas vers la position du clic sur la minimap."""
        self.xview_moveto(x)
        self.yview_moveto(y)

    def move_to_with_model_coords(self, x: float, y: float) -> None:
        """Déplace le canvas de jeu à une position donnée
        :param x: La position x en 0.0 - 1.0
        :param y: La position y en 0.0 - 1.0
        """

        """ Bouge le canvas vers la position du clic sur la minimap."""
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        x_view = (x - canvas_width/2) / 9000
        y_view = (y - canvas_height/2) / 9000

        self.xview_moveto(x_view)
        self.yview_moveto(y_view)

    def drag(self, event):
        """Déplace le canvas de jeu en fonction de la position de la souris
        :param event: L'événement de la souris"""
        self.scan_dragto(event.x, event.y, gain=1)

    def horizontal_scroll(self, event):
        """Effectue un scroll horizontal sur le canvas."""
        self.xview_scroll(-1 * int(event.delta / 120), "units")

    def vertical_scroll(self, event):
        """Effectue un scroll vertical sur le canvas."""
        self.yview_scroll(-1 * int(event.delta / 120), "units")

    def generate_background(self, n: int):
        """Genère un background de n étoiles de tailles aléatoires
        :param n: Le nombre d'étoiles à générer"""
        self.update_idletasks()
        for i in range(n):
            x, y = random.randrange(9000), random.randrange(9000)
            size = random.randrange(3) + 1
            col = random.choice(["lightYellow", "lightBlue", "lightGreen"])

            self.create_oval(x - size, y - size, x + size, y + size,
                             fill=col, tags="background")

    def generate_etoile(self, star, tag: str):
        """Créé une étoile sur le canvas.
        :param star: L'étoile à créer
        :param tag: Un tag de l'étoile"""
        print("star_generated")
        photo = self.photo_cache[star.couleur]

        photo = photo.resize((star.taille * 12, star.taille * 12),
                             Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(photo)

        self.cache.append(photo)

        self.create_image(star.x, star.y, image=photo,
                          tags=(tag,
                                star.id,
                                star.proprietaire))

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
                         tags=(StringTypes.TROUDEVERS.value,
                               porte.id, parent_id))


class SideBar(Frame):
    """ Représente la sidebar du jeu."""

    def __init__(self, master):
        """Initialise la sidebar"""
        super().__init__(master)
        self.configure(bg=hexDark, bd=1,
                       relief="solid")

        self.planet_frame = Frame(self, bg=hexDark, bd=1,
                                  relief="solid")

        self.planet_label = Label(self.planet_frame, text="Planet",
                                  bg=hexDark, fg="white",
                                  font=("Fixedsys", 20))

        self.armada_frame = Frame(self, bg=hexDark, bd=1,
                                  relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.armada_label = Label(self.armada_frame, text="Armada",
                                  bg=hexDark, fg="white",
                                  font=("Fixedsys", 20))
        """Représente le label de la vue du jeu contenant les informations"""

        self.minimap_frame = Frame(self, bg=hexDark, bd=1,
                                   relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.minimap_label = Label(self.minimap_frame, text="Minimap",
                                   bg=hexDark, fg="white",
                                   font=("Fixedsys", 20))
        """Représente le label de la vue du jeu contenant les informations"""
        self.minimap = Minimap(self.minimap_frame)
        """Représente le lbel de la vue du jeu contenant les informations"""

        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.grid_propagate(False)

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

        self.minimap_frame.grid_rowconfigure(0, weight=1, minsize=40)
        self.minimap_frame.grid_columnconfigure(0, weight=1)
        self.minimap_frame.grid_rowconfigure(1, weight=4)
        self.minimap_frame.grid_rowconfigure(2, weight=1, minsize=20)

        self.minimap_label.grid(row=0, column=0, sticky="nsew")
        self.minimap.grid(row=1, column=0, sticky="nsew")
        self.minimap.grid_propagate(False)

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

    def __init__(self, master):
        """Initialise la minimap"""
        super().__init__(master, bg=hexDark, bd=1,
                         relief="solid", highlightthickness=0)
        self.propagate(False)
        self.after_id: None or int = None

        self.x_ratio = self.winfo_width() / 9000
        self.y_ratio = self.winfo_height() / 9000

        self.bind("<Configure>", self.on_resize)

    def refresh(self, mod: Modele):
        """Rafraichit la minimap avec les données du model"""
        self.delete("all")
        for star in mod.etoiles:
            self.create_oval(star.x * self.x_ratio - 2,
                             star.y * self.y_ratio - 2,
                             star.x * self.x_ratio + 2,
                             star.y * self.y_ratio + 2,
                             fill="grey", tags=StringTypes.ETOILE.value,
                             outline=hexSpaceBlack)

        for key in mod.joueurs:
            for star in mod.joueurs[key].etoiles_controlees:
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
                                 fill="purple",
                                 tags=StringTypes.TROUDEVERS.value,
                                 outline=hexSpaceBlack)

                self.create_oval(wormhole.porte_b.x * self.x_ratio - 2,
                                 wormhole.porte_b.y * self.y_ratio - 2,
                                 wormhole.porte_b.x * self.x_ratio + 2,
                                 wormhole.porte_b.y * self.y_ratio + 2,
                                 fill="purple",
                                 tags=StringTypes.TROUDEVERS.value,
                                 outline=hexSpaceBlack)

    def on_resize(self, _):
        if self.after_id is not None:
            self.after_cancel(self.after_id)

        self.after_id = self.after(100, self.do_resize)

    def do_resize(self):
        width = self.winfo_width()
        height = self.winfo_height()

        self.old_x_ratio = self.x_ratio
        self.old_y_ratio = self.y_ratio

        self.x_ratio = width / 9000
        self.y_ratio = height / 9000

        items = [
            (StringTypes.ETOILE.value, "grey"),
            (StringTypes.TROUDEVERS.value, "purple")
        ]

        for tag, color in items:
            for star in self.find_withtag(tag):
                new_x1, new_y1, \
                    new_x2, \
                    new_y2 = self.get_new_star_position(*self.coords(star))
                self.delete(star)
                self.create_oval(new_x1, new_y1, new_x2, new_y2,
                                 fill=color, tags=tag, outline=hexSpaceBlack)

        for star in self.find_withtag("etoile_controlee"):
            new_x1, new_y1, \
                new_x2, new_y2 = self.get_new_star_position(*self.coords(star))
            color = self.itemcget(star, "fill")
            self.delete(star)
            self.create_oval(new_x1, new_y1, new_x2, new_y2,
                             fill=color, tags="etoile_controlee",
                             outline=hexSpaceBlack)

    def get_new_star_position(self, x1, y1, x2, y2):
        return x1 * self.x_ratio / self.old_x_ratio, \
               y1 * self.y_ratio / self.old_y_ratio, \
               x2 * self.x_ratio / self.old_x_ratio, \
               y2 * self.y_ratio / self.old_y_ratio


class Hud(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=hexDark, bd=1, relief="solid")

        for i in range(1):  # configure HUD columns
            self.grid_columnconfigure(i)
        self.grid_rowconfigure(0, weight=1)
        self.grid_propagate(False)

        self.ressource_frame = Frame(self, bg=hexDark, bd=1, relief="solid")
        self.ressource_frame.grid(row=0, column=0, sticky="nsew")

        for i in range(4):  # separate ressources in 4 columns
            self.ressource_frame.grid_columnconfigure(i, weight=1)
        self.ressource_frame.rowconfigure(0, weight=1)

        # FRAME ATTRIBUTES
        self.padx = 10
        self.pady = 0
        self.border = 1  # binary value

        metal_frame = Frame(self.ressource_frame, bg="#a84632", bd=self.border,
                            relief="solid",
                            padx=10)
        metal_frame.grid(row=0, column=0, sticky="ew", padx=self.padx,
                         pady=self.pady)

        beton_frame = Frame(self.ressource_frame, bg="#364b8f", bd=self.border,
                            relief="solid",
                            padx=10)
        beton_frame.grid(row=0, column=1, sticky="ew", padx=self.padx,
                         pady=self.pady)

        energy_frame = Frame(self.ressource_frame, bg="#adba59",
                             bd=self.border, relief="solid",
                             padx=10)
        energy_frame.grid(row=0, column=2, sticky="ew", padx=self.padx,
                          pady=self.pady)

        food_frame = Frame(self.ressource_frame, bg="#3f9160", bd=self.border,
                           relief="solid",
                           padx=10)
        food_frame.grid(row=0, column=3, sticky="ew", padx=self.padx,
                        pady=self.pady)

        # LABEL ATTRIBUTES

        self.ressource_height = 2
        self.ressource_width = 10
        self.text_size = 17

        self.food_text = "Food : 0"
        self.energy_text = "Energy : 0"
        self.beton_text = "Beton : 0"
        self.metal_text = "Metal : 0"

        self.metal_label = Label(metal_frame, text=self.metal_text,
                                 bg="#a84632", fg="white",
                                 font=("Fixedsys", self.text_size),
                                 width=self.ressource_width,
                                 height=self.ressource_height)

        self.beton_label = Label(beton_frame, text=self.beton_text,
                                 bg="#364b8f", fg="white",
                                 font=("Fixedsys", self.text_size),
                                 width=self.ressource_width,
                                 height=self.ressource_height)

        self.energy_label = Label(energy_frame, text=self.energy_text,
                                  bg="#adba59", fg="white",
                                  font=("Fixedsys", self.text_size),
                                  width=self.ressource_width,
                                  height=self.ressource_height)

        self.food_label = Label(food_frame, text=self.food_text, bg="#3f9160",
                                fg="white", font=("Fixedsys", self.text_size),
                                width=self.ressource_width,
                                height=self.ressource_height)

        self.show()

        self.metal_label.pack()
        self.beton_label.pack()
        self.energy_label.pack()
        self.food_label.pack()

    def update_ressources(self, metal, beton, energie, nourriture):
        self.metal_text = "Metal: " + str(metal)
        self.beton_text = "Beton: " + str(beton)
        self.energy_text = "Energy: " + str(energie)
        self.food_text = "Food: " + str(nourriture)

        self.metal_label.config(text=self.metal_text)
        self.beton_label.config(text=self.beton_text)
        self.energy_label.config(text=self.energy_text)
        self.food_label.config(text=self.food_text)

    def show(self):
        self.metal_label.config(text=self.metal_text)
        self.beton_label.config(text=self.beton_text)
        self.energy_label.config(text=self.energy_text)
        self.food_label.config(text=self.food_text)

class MiniGameWindow(Frame):

    def __init__(self, master,  proprietaire: str):
        super().__init__(master, bg=hexDarkGrey, bd=2, relief="solid",
                         width=500, height=500)

        self.is_shown: bool = False

        self.header_frame: Frame = Frame(self, bg=hexDarkGrey,
                                         bd=1, relief="solid")
        self.title_label = Label(self.header_frame, text="HEADER",
                                        bg=hexDarkGrey, fg="white",
                                        font=("Fixedsys", 15))

        self.main_frame: Frame = Frame(self, bg=hexDarkGrey,
                                       bd=1, relief="solid")
        self.minigame_label = Label(self.main_frame, text="MINIGAME",
                                    bg=hexDarkGrey, fg="white",
                                    font=("Fixedsys", 13))

        self.place_header()
        self.place_main()

    def show(self) -> None:
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.is_shown = True

    def hide(self) -> None:
        """Cache la fenetre"""
        self.place_forget()
        self.is_shown = False

    def place_header(self) -> None:
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        self.title_label.place(anchor="center", relx=0.5, rely=0.5)

    def place_main(self) -> None:
        # Start with the main frame
        self.main_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
        self.minigame_label.place(anchor="center", relx=0.5, rely=0.5)

        minigame = Minigame(self.minigame_label)
        minigame.game1()
        minigame.pack()



class Minigame(Frame):

    def __init__(self, master, *args):
        super().__init__(master, bg=hexDark, bd=1, relief="solid",
                         width=400, height=350, *args)

    def game1(self):
        self.minigame_frame = Frame(self, bg=hexDarkGrey, bd=1, relief="solid")
        self.minigame_frame.place(relx=0.5, rely=0.3, relwidth=0.4, relheight=0.15, anchor="center")

        self.textLabel = Label(self.minigame_frame, text="123456",
                               bg=hexDarkGrey, fg="white",
                               font=("Fixedsys", 18))
        self.textLabel.place(relx=0.5, rely=0.5, anchor="center")


        self.input_frame = Frame(self, bg=hexDarkGrey, bd=1, relief="solid")
        self.input_frame.place(relx=0.5, rely=0.6, relwidth=0.45, relheight=0.25, anchor="center")

        self.input_text = Text(self.input_frame, height=1, width=10,
                               bg=hexDarkGrey, fg="white", bd=1, relief="solid",
                               font=("Fixedsys", 17))
        self.input_text.place(relx=0.5, rely=0.3, anchor="center")

        self.input_button = tkinter.Button(self.input_frame, text="input") #TODO: add command attribute to link input
        self.input_button.place(relx=0.5, rely=0.75, anchor="center")




class ChatBox(Frame):
    def __init__(self):
        super().__init__()
        self.configure(bg=hexDark, bd=1, relief="solid", height=200, width=400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.chat_frame = Frame(self, bg=hexDark, bd=1, relief="solid")
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_text = Text(self.chat_frame, bg=hexDark, fg="white", bd=0,
                              relief="solid", height=10, width=50)
        self.chat_text.grid(row=0, column=0, sticky="nsew")
        self.chat_text.insert(END, "Bienvenue sur le chat !\n")
        self.chat_entry = Entry(self, bg=hexDark, fg="white", bd=-1, width=50)
        self.chat_entry.grid(row=1, column=0, sticky="nsew")
        self.chat_entry.bind("<Return>", self.send_message)

    def send_message(self, _):
        message = self.chat_entry.get()
        self.chat_text.insert(END, message + "\n")
        self.chat_entry.delete(0, END)


class MouseOverView(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=hexDark, bd=1, relief="solid")
        self.visible = False
        self.updated = False
        self.id = None

    def on_mouse_over(self, *args):
        if not self.updated:
            dictlist = []
            for dict in args:
                if dict is not None:
                    dictlist.append(dict)
            for i in range(len(dictlist)):
                container = Frame(self, bg=hexDark, bd=1, relief="solid",
                                  pady=10)
                # add a max size with :
                container.grid(row=i, column=0, sticky="nsew")
                title = Label(container, text=dictlist[i].pop("header"),
                              bg=hexDark, fg="white", font=("Fixedsys", 15),
                              pady=2)
                title.grid(row=0, column=0, sticky="nsew")
                for j, (key, value) in enumerate(dictlist[i].items()):
                    label = Label(container, text=key + " : " + str(value),
                                  bg=hexDark, fg="white", font=("Fixedsys", 10),
                                  pady=2, wraplength=250)
                    label.grid(row=j + 1, column=0, sticky="nsew")

            self.updated = True

    def hide(self, _):
        self.visible = False
        self.updated = False
        self.destroy()

    def show(self, event):
        self.id = event.widget.find_withtag("current")[0]
        self.visible = True

        x = event.x
        y = event.y

        # If it gets out of the window, it will be placed on the left
        if x + self.winfo_width() > event.widget.winfo_width():
            x = event.widget.winfo_width() - self.winfo_width()
        # If it gets out of the window, it will be placed on the top
        if y + self.winfo_height() > event.widget.winfo_height():
            y = event.widget.winfo_height() - self.winfo_height()

        self.place(x=x, y=y)


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


if __name__ == '__main__':
    root = Tk()
    root.geometry("800x600")

    minigamewindow = MiniGameWindow(root, "Bob")
    minigamewindow.pack()

    root.mainloop()




