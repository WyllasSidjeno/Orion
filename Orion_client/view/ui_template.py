from __future__ import annotations

from tkinter import Frame, Label, Canvas, Text, Entry, Button, Tk, NW
from typing import TYPE_CHECKING

from PIL import Image
from PIL import ImageTk

from Orion_client.helpers.CommandQueues import ControllerQueue
from Orion_client.helpers.helper import StringTypes
from Orion_client.model.ships import Ship
from Orion_client.view.star_template import EtoileWindow
from Orion_client.view.view_common_ressources import *

if TYPE_CHECKING:
    from Orion_client.model.modele import Modele
    from Orion_client.model.space_object import PorteDeVers


class GameCanvas(Canvas):
    """ Représente le canvas de jeu, ce qui veux dire l'ensemble des
    planetes, vaisseaux spaciaux et autres objets du jeu qui ne sont
    pas des menus ou des fenetres ou de l'information
    """
    username: str
    command_queue: ControllerQueue

    def __init__(self, master, proprietaire):
        """Initialise le canvas de jeu
        :param master: la fenetre principale
        :param proprietaire: le proprietaire du canvas de jeu
        """
        backgroud_image: Image
        super().__init__(master)
        self.configure(bg=Color.spaceBlack.value, bd=1,
                       relief="solid", highlightthickness=0)

        self.etoile_window = EtoileWindow(master, proprietaire)
        """Représente la fenêtre de planète de la vue du jeu."""
        self.etoile_window.hide()

        self.photo_cache = {
            "white": Image.open("assets/planet/star_white01.png"),
            "blue": Image.open("assets/planet/star_blue01.png"),
            "red": Image.open("assets/planet/star_red01.png"),
            "yellow": Image.open("assets/planet/star_yellow01.png"),
            "orange": Image.open("assets/planet/star_orange01.png"),
            "background": Image.open("assets/background/background.jpeg"),
            "militaire": Image.open("assets/ships/fighter.png"),
            "reconnaissance": Image.open("assets/ships/reconnaissance.png"),
            "transportation": Image.open("assets/ships/transportation.png"),
        }
        for key, photo in self.photo_cache.items():
            if key != "background":
                photo.thumbnail((100, 100), Image.ANTIALIAS)
            else:
                photo.thumbnail((1000, 1000), Image.ANTIALIAS)

        self.cache = []

        self.mouse_over_view = MouseOverView(self)

        self.bind("<B1-Motion>", self.mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_stop_drag)

        self.initial_x_move: int | None = None
        self.initial_y_move: int | None = None
        self.dx = 0
        self.dy = 0

        self.bounding_box = BoundingBox(0, 0, 0, 0)

        self.moved: bool = True

        self.bind("<Configure>", self.on_resize)
        self.tag_bind(StringTypes.ETOILE.value, "<Enter>",
                      self.on_etoile_enter)

    def on_etoile_enter(self, event):
        self.mouse_over_view.show(event)
        self.tag_unbind(StringTypes.ETOILE.value, "<Enter>")
        self.tag_bind(StringTypes.ETOILE.value, "<Leave>",
                      self.on_etoile_leave)

    def on_etoile_leave(self, event):
        self.mouse_over_view.hide(event)
        self.tag_unbind(StringTypes.ETOILE.value, "<Leave>")
        self.tag_bind(StringTypes.ETOILE.value, "<Enter>",
                      self.on_etoile_enter)

    def mouse_drag(self, event):
        """Déplace le canvas de jeu en fonction de la souris"""
        if self.initial_x_move is None:
            self.initial_x_move = event.x
            self.initial_y_move = event.y
        if self.mouse_over_view.visible:
            self.mouse_over_view.hide("arg")

        self.dx = event.x - self.initial_x_move
        self.dy = event.y - self.initial_y_move

        self.moved = True

    def on_mouse_stop_drag(self, _):
        """Déplace le canvas de jeu en fonction de la souris"""
        self.initial_x_move = None
        self.initial_y_move = None

        self.dx = 0
        self.dy = 0

    def refresh(self, mod: Modele):
        """Rafrachit le canvas de jeu avec les données du model
        :param mod: Le model"""
        self.focus()
        if self.moved:
            x = self.bounding_box.x + self.dx
            y = self.bounding_box.y + self.dy
            width = x + self.winfo_width()
            height = y + self.winfo_height()

            x_diff = width - x
            y_diff = height - y

            x = max(min(x, 9000 - x_diff), 0)
            y = max(min(y, 9000 - y_diff), 0)
            width = max(min(width, 9000), 0)
            height = max(min(height, 9000), 0)

            self.bounding_box.update(x, y, width, height)

        self.cache = []

        self.delete(StringTypes.ETOILE.value)
        self.delete(StringTypes.ETOILE_OCCUPEE.value)
        self.delete(StringTypes.TROUDEVERS.value)
        self.delete(StringTypes.VAISSEAU.value)

        for etoile in mod.get_etoiles_in_view(*self.bounding_box.__tuple__()):
            self.generate_etoile(etoile)

        for porte in mod.get_porte_de_vers_in_view(
                *self.bounding_box.__tuple__()):
            self.generate_porte_de_vers(porte)

        for vaisseau in mod.get_vaisseau_in_view(
                *self.bounding_box.__tuple__()):
            self.generate_vaisseau(vaisseau)

        if self.mouse_over_view.visible:
            obj = mod.get_object(self.mouse_over_view.id)
            self.mouse_over_view.on_mouse_over(obj.to_mouse_over_dict())

    def generate_porte_de_vers(self, porte: PorteDeVers):

        x = porte.x - self.bounding_box.x
        y = porte.y - self.bounding_box.y

        self.create_oval(x - porte.pulse, y - porte.pulse,
                         x + porte.pulse, y + porte.pulse,
                         fill="black",
                         tags=(porte.id, StringTypes.TROUDEVERS.value))

    def generate_vaisseau(self, vaisseau: Ship):
        x = vaisseau.position[0] - self.bounding_box.x
        y = vaisseau.position[1] - self.bounding_box.y
        if vaisseau.type() == "transportation":
            largeur = 4
            longueur = 8
        elif vaisseau.type() == "militaire":
            largeur = 6
            longueur = 6
        else:
            largeur = 4
            longueur = 6

        photo = self.photo_cache[vaisseau.type()]

        photo = photo.rotate(vaisseau.angle, expand=True)
        if vaisseau.angle % 180 == 90:
            largeur, longueur = longueur, largeur

        photo = photo.resize((largeur * 12, longueur * 12),
                             Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(photo)
        self.cache.append(photo)

        self.create_image(x, y, image=photo,
                          tags=(StringTypes.VAISSEAU.value, vaisseau.id,
                                vaisseau.proprietaire, vaisseau.type()))

    def generate_etoile(self, star):
        """Créé une étoile sur le canvas.
        :param star: L'étoile à créer"""
        photo = self.photo_cache[star.couleur]

        photo = photo.resize((star.taille * 12, star.taille * 12),
                             Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(photo)
        self.cache.append(photo)

        star_x = star.x - self.bounding_box.x
        star_y = star.y - self.bounding_box.y
        if star.proprietaire == "":
            tag = StringTypes.ETOILE.value
        else:
            tag = StringTypes.ETOILE_OCCUPEE.value

        self.create_image(star_x, star_y, image=photo,
                          tags=(tag,
                                star.id,
                                star.proprietaire)
                          )

    def move_to(self, rel_x, rel_y):
        """Déplace le canvas à la position x et y
        """

        x = rel_x * 9000
        y = rel_y * 9000

        width = x + self.winfo_width()
        height = y + self.winfo_height()

        x_diff = width - x
        y_diff = height - y

        x = max(min(x, 9000 - x_diff), 0)
        y = max(min(y, 9000 - y_diff), 0)
        width = max(min(width, 9000), 0)
        height = max(min(height, 9000), 0)

        self.bounding_box.update(x, y, width, height)
        self.moved = True

    def on_resize(self, event):
        """Méthode appelée lorsqu'on redimensionne la fenêtre.
        :param event: L'événement"""
        background_image = self.photo_cache["background"]
        background_image = background_image.resize((event.width, event.height),
                                                   Image.ANTIALIAS)
        self.background_image = ImageTk.PhotoImage(background_image)

        background = self.create_image(0, 0, anchor=NW,
                                       image=self.background_image)
        self.tag_lower(background)


class SideBar(Frame):
    """ Représente la sidebar du jeu."""

    def __init__(self, master):
        """Initialise la sidebar"""
        super().__init__(master)
        self.configure(bg=Color.dark.value, bd=1,
                       relief="solid")

        self.planet_frame = Frame(self, bg=Color.dark.value, bd=1,
                                  relief="solid")

        self.planet_label = Label(self.planet_frame, text="Planet",
                                  bg=Color.dark.value, fg="white",
                                  font=(police, 20))

        self.armada_frame = Frame(self, bg=Color.dark.value, bd=1,
                                  relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.armada_label = Label(self.armada_frame, text="Armada",
                                  bg=Color.dark.value, fg="white",
                                  font=(police, 20))
        """Représente le label de la vue du jeu contenant les informations"""

        self.minimap_frame = Frame(self, bg=Color.dark.value, bd=1,
                                   relief="solid")
        """Représente le cadre de la vue du jeu contenant les informations"""
        self.minimap_label = Label(self.minimap_frame, text="Minimap",
                                   bg=Color.dark.value, fg="white",
                                   font=(police, 20))
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
        super().__init__(master, bg=Color.dark.value, bd=1,
                         relief="solid", highlightthickness=0)
        self.propagate(False)
        self.after_id: None or int = None

        self.x_ratio = self.winfo_width() / 9000
        self.y_ratio = self.winfo_height() / 9000
        self.user_square = self.create_rectangle(0, 0, 0, 0,
                                                 fill="white", outline="white")

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
                             outline=Color.spaceBlack.value)

        for key in mod.joueurs:
            for star in mod.joueurs[key].etoiles_controlees:
                self.create_oval(star.x * self.x_ratio - 2,
                                 star.y * self.y_ratio - 2,
                                 star.x * self.x_ratio + 2,
                                 star.y * self.y_ratio + 2,
                                 fill=mod.joueurs[key].couleur,
                                 tags="etoile_controlee",
                                 outline=Color.spaceBlack.value)

            """for wormhole in mod.trou_de_vers:
                self.create_oval(wormhole.porte_a.x * self.x_ratio - 2,
                                 wormhole.porte_a.y * self.y_ratio - 2,
                                 wormhole.porte_a.x * self.x_ratio + 2,
                                 wormhole.porte_a.y * self.y_ratio + 2,
                                 fill="purple",
                                 tags=StringTypes.TROUDEVERS.value,
                                 outline=Color.spaceBlack.value)

                self.create_oval(wormhole.porte_b.x * self.x_ratio - 2,
                                 wormhole.porte_b.y * self.y_ratio - 2,
                                 wormhole.porte_b.x * self.x_ratio + 2,
                                 wormhole.porte_b.y * self.y_ratio + 2,
                                 fill="purple",
                                 tags=StringTypes.TROUDEVERS.value,
                                 outline=Color.spaceBlack.value)"""

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
                                 fill=color, tags=tag,
                                 outline=Color.spaceBlack.value)

        for star in self.find_withtag("etoile_controlee"):
            new_x1, new_y1, \
                new_x2, new_y2 = self.get_new_star_position(*self.coords(star))
            color = self.itemcget(star, "fill")
            self.delete(star)
            self.create_oval(new_x1, new_y1, new_x2, new_y2,
                             fill=color, tags="etoile_controlee",
                             outline=Color.spaceBlack.value)

    def get_new_star_position(self, x1, y1, x2, y2):
        return x1 * self.x_ratio / self.old_x_ratio, \
               y1 * self.y_ratio / self.old_y_ratio, \
               x2 * self.x_ratio / self.old_x_ratio, \
               y2 * self.y_ratio / self.old_y_ratio

    def user_square_move(self, pos):
        x1, y1, x2, y2 = pos
        x1 *= self.x_ratio
        y1 *= self.y_ratio
        x2 *= self.x_ratio
        y2 *= self.y_ratio

        self.user_square = self.create_rectangle(x1, y1, x2, y2,
                                                 outline="white")


class Hud(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=Color.dark.value, bd=1, relief="solid")

        self.grid_columnconfigure(0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_propagate(False)

        self.ressource_frame = Frame(self, bg=Color.dark.value, bd=1,
                                     relief="solid")
        self.ressource_frame.grid(row=0, column=0, sticky="nsew")

        for i in range(4):  # separate ressources in 4 columns
            self.ressource_frame.grid_columnconfigure(i, weight=1)
        self.ressource_frame.rowconfigure(0, weight=1)

        # FRAME ATTRIBUTES
        padx = 10
        border_size = 1

        metal_frame = Frame(self.ressource_frame, bg="#a84632",
                            bd=border_size, relief="solid"
                            )
        metal_frame.grid(row=0, column=0, sticky="ew",
                         padx=padx, pady=padx
                         )

        beton_frame = Frame(self.ressource_frame, bg="#364b8f",
                            bd=border_size, relief="solid"
                            )
        beton_frame.grid(row=0, column=1, sticky="ew",
                         padx=padx, pady=padx
                         )

        energy_frame = Frame(self.ressource_frame, bg="#adba59",
                             bd=border_size, relief="solid"
                             )
        energy_frame.grid(row=0, column=2, sticky="ew",
                          padx=padx, pady=padx
                          )

        food_frame = Frame(self.ressource_frame, bg="#3f9160",
                           bd=border_size, relief="solid"
                           )
        food_frame.grid(row=0, column=3, sticky="ew",
                        padx=padx, pady=padx
                        )

        self.ressource_height = 1
        self.ressource_width = 7
        self.text_size = 16

        self.metal_header = Label(metal_frame, text="Metal", bg="#a84632",
                                  height=self.ressource_height,
                                  width=self.ressource_width,
                                  font=(police, self.text_size)
                                  )
        self.beton_header = Label(beton_frame, text="Beton", bg="#364b8f",
                                  height=self.ressource_height,
                                  width=self.ressource_width,
                                  font=(police, self.text_size)
                                  )
        self.energy_header = Label(energy_frame, text="Energy", bg="#adba59",
                                   height=self.ressource_height,
                                   width=self.ressource_width,
                                   font=(police, self.text_size),
                                   )
        self.food_header = Label(food_frame, text="Food", bg="#3f9160",
                                 height=self.ressource_height,
                                 width=self.ressource_width,
                                 font=(police, self.text_size)
                                 )

        self.metal_info = Label(metal_frame, text="0", bg="#a84632",
                                height=self.ressource_height,
                                width=self.ressource_width,
                                font=(police, self.text_size)
                                )
        self.beton_info = Label(beton_frame, text="0", bg="#364b8f",
                                height=self.ressource_height,
                                width=self.ressource_width,
                                font=(police, self.text_size)
                                )
        self.energy_info = Label(energy_frame, text="0", bg="#adba59",
                                 height=self.ressource_height,
                                 width=self.ressource_width,
                                 font=(police, self.text_size)
                                 )
        self.food_info = Label(food_frame, text="0", bg="#3f9160",
                               height=self.ressource_height,
                               width=self.ressource_width,
                               font=(police, self.text_size)
                               )

        self.metal_header.grid(row=0, column=0, sticky="ew")
        self.beton_header.grid(row=0, column=0, sticky="ew")
        self.energy_header.grid(row=0, column=0, sticky="ew")
        self.food_header.grid(row=0, column=0, sticky="ew")

        self.metal_info.grid(row=1, column=0, sticky="new")
        self.beton_info.grid(row=1, column=0, sticky="new")
        self.energy_info.grid(row=1, column=0, sticky="new")
        self.food_info.grid(row=1, column=0, sticky="new")

        self.science_frame = Frame(self, bg=Color.dark.value, bd=1,
                                   relief="solid")
        self.science_frame.grid(row=0, column=1, sticky="e", padx=10)
        self.science_frame.grid_columnconfigure(0, weight=1)
        self.science_frame.grid_rowconfigure(0, weight=1)

        self.science_button = Button(self.science_frame, text="Science",
                                     bg=Color.dark.value, fg="white",
                                     font=("Fixedsys", self.text_size),
                                     width=self.ressource_width,
                                     height=self.ressource_height)
        self.science_button.grid(row=0, column=0, sticky="nes")

    def update_ressources(self, metal, beton, energie, nourriture):
        self.metal_info.config(text=metal)
        self.beton_info.config(text=beton)
        self.energy_info.config(text=energie)
        self.food_info.config(text=nourriture)


class MiniGameWindow(Frame):

    def __init__(self, master, proprietaire: str):
        super().__init__(master, bg=Color.darkGrey.value, bd=2, relief="solid",
                         width=500, height=500)

        self.is_shown: bool = False

        self.header_frame: Frame = Frame(self, bg=Color.darkGrey.value,
                                         bd=1, relief="solid")
        self.title_label = Label(self.header_frame, text="HEADER",
                                 bg=Color.darkGrey.value, fg="white",
                                 font=("Fixedsys", 15))

        self.main_frame: Frame = Frame(self, bg=Color.darkGrey.value,
                                       bd=1, relief="solid")
        self.minigame_label = Label(self.main_frame, text="MINIGAME",
                                    bg=Color.darkGrey.value, fg="white",
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
        super().__init__(master, bg=Color.dark.value, bd=1, relief="solid",
                         width=400, height=350, *args)

    def game1(self):  # remember the number
        self.minigame_frame = Frame(self, bg=Color.darkGrey.value, bd=1,
                                    relief="solid")
        self.minigame_frame.place(relx=0.5, rely=0.3, relwidth=0.4,
                                  relheight=0.15, anchor="center")

        self.answerLabel = Label(self.minigame_frame, text="123456",
                                 bg=Color.darkGrey.value, fg="white",
                                 font=("Fixedsys", 18))
        self.answerLabel.place(relx=0.5, rely=0.5, anchor="center")

        self.input_frame = Frame(self, bg=Color.darkGrey.value, bd=1,
                                 relief="solid")
        self.input_frame.place(relx=0.5, rely=0.6, relwidth=0.45,
                               relheight=0.25, anchor="center")

        self.input_text = Text(self.input_frame, height=1, width=10,
                               bg=Color.darkGrey.value, fg="white", bd=1,
                               relief="solid",
                               font=("Fixedsys", 17))
        self.input_text.place(relx=0.5, rely=0.3, anchor="center")

        self.input_button = Button(self.input_frame,
                                   text="input")  # TODO: add command attribute to link input
        self.input_button.place(relx=0.5, rely=0.75, anchor="center")

    def game2(self):  # simon says
        self.minigame_frame = Frame(self, bg=Color.darkGrey.value, bd=1,
                                    relief="solid")
        self.minigame_frame.place(relx=0.5, rely=0.5, anchor="center")

        # for i in range(9):

    def game3(self):  # target practice
        print("")

    def game4(self):  # solo pong
        print("")


class ChatBox(Frame):
    def __init__(self, master, queue):
        super().__init__(master)
        self.queue = queue
        self.configure(bg=Color.dark.value, bd=1, relief="solid", height=200,
                       width=400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.chat_frame = Frame(self, bg=Color.dark.value, bd=1,
                                relief="solid")
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_text = Text(self.chat_frame, bg=Color.dark.value, fg="white",
                              bd=0,
                              relief="solid", height=10, width=50)
        self.chat_text.grid(row=0, column=0, sticky="nsew")

        self.chat_text.bind("<Button-1>", lambda _: "break")

        self.chat_entry = Entry(self, bg=Color.dark.value, fg="white", bd=-1,
                                width=50)
        self.chat_entry.grid(row=1, column=0, sticky="nsew")
        self.chat_entry.bind("<Return>", self.send_message)
        self.chat_entry.bind("<Escape>", self.hide)

        self.chat_text.bind("<B1-Motion>", self.follow_mouse_request)
        self.chat_text.bind("<ButtonRelease-1>", self.follow_mouse)

        self.event_id: int or None = None

    def send_message(self, _):
        if self.chat_entry.get() != "":
            self.queue.handle_message(self.chat_entry.get())
            self.chat_entry.delete(0, "end")
        else:
            self.hide(None)

    def show(self, _):
        # Put it on top of its master content
        self.place(in_=self.master, relwidth=.5, relheight=.5,
                   relx=.5, rely=.5, anchor="center")
        self.chat_entry.focus_set()

    def hide(self, _):
        # Put it back in its master content
        self.place_forget()
        self.master.focus_set()

    def follow_mouse_request(self, event):
        if self.event_id is not None:
            self.after_cancel(self.event_id)
            self.event_id = None
        self.event_id = self.after(10, self.follow_mouse, event)

    def follow_mouse(self, event):
        if self.event_id is not None:
            self.after_cancel(self.event_id)
            self.event_id = None

        self.place_configure(relx=event.x_root / self.master.winfo_width(),
                             rely=event.y_root / self.master.winfo_height())

    def refresh(self, model: Modele):
        if model.message_manager.new_messages:
            messages = model.message_manager.get_new_messages()
            for message in messages:
                self.chat_text.insert("end", message + "\n")


class MouseOverView(Frame):
    id: str or int

    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=Color.dark.value, bd=1, relief="solid")
        self.visible = False
        self.modulo = 30
        self.current_modulo = 30

    def on_mouse_over(self, *args):
        if self.modulo == self.current_modulo:
            self.current_modulo = 0
            dictlist = []
            for dict in args:
                if dict is not None:
                    dictlist.append(dict)

            for i in range(len(dictlist)):
                container = Frame(self, bg=Color.dark.value, bd=1,
                                  relief="solid",
                                  pady=10)
                # add a max size with :
                container.grid(row=i, column=0, sticky="nsew")
                title = Label(container, text=dictlist[i].pop("header"),
                              bg=Color.dark.value, fg="white",
                              font=(police, 15),
                              pady=2)
                title.grid(row=0, column=0, sticky="nsew")
                for j, (key, value) in enumerate(dictlist[i].items()):
                    label = Label(container, text=key + " : " + str(value),
                                  bg=Color.dark.value, fg="white",
                                  font=(police, 10),
                                  pady=2, wraplength=250)
                    label.grid(row=j + 1, column=0, sticky="nsew")
        else:
            self.current_modulo += 1

    def hide(self, _):
        self.visible = False
        self.current_modulo = 30
        self.place_forget()

    def show(self, event):
        self.id = event.widget.find_withtag("current")[0]
        self.id = event.widget.gettags(self.id)[1]
        self.visible = True

        x = event.x
        y = event.y

        # If it gets out of the window, it will be placed on the left
        if x + self.winfo_width() > event.widget.winfo_width():
            x = event.widget.winfo_width() - self.winfo_width()
        # If it gets out of the window, it will be placed on the top
        if y + self.winfo_height() > event.widget.winfo_height():
            y = event.widget.winfo_height() - self.winfo_height()

        # add an offset so the cursor is not on the frame
        x += 10
        y += 10

        self.place(x=x, y=y)


if __name__ == '__main__':
    root = Tk()
    root.geometry("800x600")

    minigamewindow = MiniGameWindow(root, "Bob")
    minigamewindow.pack()

    root.mainloop()
