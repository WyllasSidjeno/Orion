"""Module qui contient la classe Science et Science Tree"""
import tkinter as tk
from Orion_client.helpers.helper import AlwaysInt
from Orion_client.view.view_common_ressources import *

hexDarkGreen: str = "#0A6522"
"""Couleur des sciences debloquer"""
hexGreyGreen: str = "#444C38"
"""Couleur des sciences bloquer"""
hexYellowGreen: str = "#C7EA46"
"""Couleur des sciences prochaines a debloquer"""
hexGrey: str = "#2f3136"
"""Couleur des borders des cases sciences"""
hexBrightYellow: str = "#F7CE25"
"""Couleur border buyScience"""
hexBrightGreen: str = "#cbff00"
"""Couleur bouton oui"""
hexRed: str = "#ff5200"
"""Couleur bouton annuler"""


class ArbreScience:
    """Classe qui contient l'arbre de science"""
    niveau_vaisseau_dispo = AlwaysInt(0)  # niveau de vaisseau débloqué
    niveau_batiment_dispo = AlwaysInt(0)  # niveau de bâtiment débloqué
    science_acquise = AlwaysInt(0)
    sciences: dict = {'science_0': [0, 4, "available"], 'science_1': [1, 5, "available"], 'science_2':
        [2, 8, "unlockable"], 'science_3': [3, 9, "unlockable"], 'science_4': [4, 10, "blocked"]
        , 'science_5': [5, 11, "blocked"], 'science_6': [6, 13, "blocked"], 'science_7': [7, 15, "blocked"]}

    def __init__(self):
        """Constructeur de la classe"""
        self.root = root

        self.science_points = AlwaysInt(6)  # points de science

    def show_science(self):
        """Affiche les sciences"""
        label = tk.Label(self.root, text="Science", bg="blue")
        label.pack()
        # fenetre science & self.science

    def science_bloquer(self):
        """Si : Affiche la case d'une science bloquée
        Sinon : Affiche la case d'une science débloquée"""
        pass

    def science_debloquer(self):
        """Affiche la case d'une science débloquée et appelle is_unlockable
        pour les sciences prochaines
        si la science suivante est débloquable"""
        pass

    def is_unlockable(self):
        """Vérifie si la science est débloquable
        si : science précédente débloquée et points de science suffisant"""
        pass

    def on_click_select(self):
        """Affiche une fenetre pour acheter la science
        button : acheter
        button : retour"""
        pass


class Controller:
    """Classe qui contient les méthodes de l'arbre de science"""
    sciences: dict = {'science_0': [0, 4, "available"], 'science_1': [1, 5, "available"], 'science_2':
        [2, 8, "unlockable"], 'science_3': [3, 9, "unlockable"], 'science_4': [4, 10, "blocked"]
        , 'science_5': [5, 11, "blocked"], 'science_6': [6, 13, "blocked"], 'science_7': [7, 15, "blocked"]}

    choixTemporaire: None
    buyScience: tk.Frame
    con_frame: tk.Frame

    def __init__(self):
        self.root = root
        self.science_points = AlwaysInt(10)  # points de science
        self.sortedDict = sorted(self.sciences.items())
        self.maxRow = AlwaysInt(0)
        self.maxColumn = AlwaysInt(4)
        self.root.config(bg=hexDarkGrey)

    def show_science(self, data):
        """Affiche les sciences"""
        for i, science in enumerate(data.sciences):
            prix = data.sciences.get(science)[1]

            if self.science_acquises(f"{science}", data):
                self.con_frame = self.case_science_format()
                lbl = tk.Label(self.con_frame, text=f"{science} prix : {prix}", height=5, width=15, bg=hexDarkGreen)
            else:
                self.con_frame = self.case_science_format()
                lbl = tk.Label(self.con_frame, text=f"{science} prix : {prix}", height=5, width=15, bg=hexGreyGreen)

            if self.science_achetable(f"{science}", data):
                self.con_frame = self.case_science_format()
                lbl = tk.Label(self.con_frame, text=f"{science} prix : {prix}", height=5, width=15, bg=hexYellowGreen)

            if i % self.maxColumn == 0 and i != 0:
                self.maxRow += 1

            setattr(self, f"{science}_{i}", self.con_frame.grid(row=self.maxRow, column=i % self.maxColumn, padx=2, pady=2))
            setattr(self, f"{science}_{i}", lbl.grid(row=self.maxRow, column=i % self.maxColumn, padx=2, pady=2))

            if self.science_achetable(f"{science}", data):
                lbl.bind("<Button-1>", self.on_click_select)
            lbl.grid(sticky='nsew')

    def science_achetable(self, science: object, data: object) -> bool:
        """Si points suffisant, niveau suffisant et is_unlockable
         : Affiche la case d'une science bloquée
         Sinon : Affiche la case d'une science débloquée"""
        # Ajouter les autres conditions ici
        if data.sciences.get(science)[2] == "unlockable":
            if data.sciences.get(science)[1] <= self.science_points:
                return True
        else:
            return False

    def science_acquises(self, science: object, data: object) -> bool:
        """Verifie si la science est acquise"""
        if data.sciences.get(science)[2] == "available":
            return True
        else:
            return False
    def case_science_format(self):
        self.con_frame = tk.Frame(self.root, bg=hexGrey, highlightbackground="black", highlightthickness=3)
        return self.con_frame

    def buy_science(self, event):
        """Achete la science"""
        # self.choixTemporaire.split(" ")[0]
        print(self.choixTemporaire.split(" ")[0])

    def on_click_select(self, event):
        """Affiche une fenetre pour acheter la science
        button : acheter
        button : annuler"""
        # if buyScience is not None: destroy the last one
        if hasattr(self, "buyScience"):
            self.buyScience.destroy()

        self.choixTemporaire = event.widget.cget("text")

        self.buyScience = tk.Frame(self.root, bg=hexDarkGrey, highlightbackground=hexBrightYellow, highlightthickness=2)
        buyLabel = tk.Label(self.buyScience, text="Buy science?", fg=hexBrightYellow, bg=hexDarkGrey, font=("Arial", 10))

        self.buyScience.place(relx=0.06, rely=0.65)
        buyLabel.place(relx=0.06, rely=0.65)

        OuiBouton = tk.Button(self.buyScience, text="Oui", width=10, height=1, bg=hexBrightGreen)
        annulerBouton = tk.Button(self.buyScience, text="Annuler", width=10, height=1, bg=hexRed,
                                  command=self.buyScience.destroy)
        OuiBouton.bind("<Button-1>", self.buy_science)

        OuiBouton.grid(row=1, column=0, sticky="nsew")
        annulerBouton.grid(row=1, column=1, sticky="nsew")
        buyLabel.grid(row=0, column=0, sticky="nsew")

    # def refresh(self, mod):
    #     self.root.refresh(mod)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Science tree")
    root.geometry("800x600")
    controller = Controller()
    controller.show_science(ArbreScience)
    root.mainloop()
