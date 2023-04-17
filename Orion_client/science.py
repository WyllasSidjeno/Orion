"""Module qui contient la classe Science et Science Tree"""
import tkinter as tk
from Orion_client.helpers.helper import AlwaysInt
from Orion_client.view.view_common_ressources import *

class ArbreScience(tk.Frame):
    """Classe qui contient l'arbre de science"""
    niveau_vaisseau_dispo = AlwaysInt(0)  # niveau de vaisseau débloqué
    niveau_batiment_dispo = AlwaysInt(0)  # niveau de bâtiment débloqué
    science_acquise = AlwaysInt(0)
    sciences: dict = {
        'science_0': [4, "acquise"],
        'science_1': [5, "acquise"],
        'science_2': [8, "unlockable"],
        'science_3': [9, "unlockable"],
        'science_4': [10, "blocked"],
        'science_5': [11, "blocked"],
        'science_6': [13, "blocked"],
        'science_7': [15, "blocked"]
    }

    choixTemporaire: str
    buyScience: tk.Frame

    def __init__(self, master, width: int = 500, height: int = 250, **kwargs):
        """Constructeur de la classe"""
        super().__init__(master, width=width, height=height, **kwargs,
                         background=hexGrey)
        self.grid_propagate(False)
        self.science_points = 10

        self.title = tk.Label(self, text="Arbre de science", bg=hexGrey,
                                fg="white", font=("Arial", 20))

        self.title.grid(row=0, column=0, sticky="nsew")

        self.science_frame = tk.Frame(self, bg=hexGrey)
        self.science_frame.grid(row=1, column=0, sticky="nsew")

        self.show_science(ArbreScience.sciences)

    def show_science(self, sciences):
        """Affiche les sciences"""
        maxRow = 0
        maxColumn = 4
        for i, science in enumerate(sciences):
            prix = sciences.get(science)[0]
            con_frame = tk.Frame(
                self.science_frame, bg=hexGrey,
                highlightbackground="black",
                highlightthickness=3
            )

            if self.science_acquises(science, sciences):
                lbl = tk.Label(con_frame, text=f"{science} prix : {prix}",
                               height=5, width=15, bg=hexDarkGreen)
            else:
                lbl = tk.Label(con_frame, text=f"{science} prix : {prix}",
                               height=5, width=15, bg=hexGreyGreen)

            if self.science_achetable(science, sciences):
                lbl = tk.Label(con_frame, text=f"{science} prix : {prix}",
                               height=5, width=15, bg=hexYellowGreen)

            if i % maxColumn == 0 and i != 0:
                maxRow += 1

            setattr(self, f"{science}_{i}",
                    con_frame.grid(row=maxRow,
                                   column=i % maxColumn, padx=2,
                                   pady=2))
            setattr(self, f"{science}_{i}",
                    lbl.grid(row=maxRow, column=i % maxColumn,
                             padx=2, pady=2))

            if self.science_achetable(science, sciences):
                lbl.bind("<Button-1>", self.on_click_select)
            lbl.grid(sticky='nsew')

    def science_acquises(self, science: str, sciences: dict) -> bool:
        """Verifie si la science est acquise"""
        if sciences[science][1] == "acquise":
            return True
        return False

    def science_achetable(self, science: str, sciences: dict) -> bool:
        """Si points suffisant, niveau suffisant et is_unlockable
         : Affiche la case d'une science bloquée
         Sinon : Affiche la case d'une science débloquée"""
        if self.science_points >= sciences[science][0]:
            return True
        return False

    def buy_science(self, event):
        """Achete la science"""
        print(self.choixTemporaire.split(" ")[0])
        self.buyScience.destroy()

    def on_click_select(self, event):
        """Affiche une fenetre pour acheter la science
        button : acheter
        button : annuler"""
        # if buyScience is not None: destroy the last one
        if hasattr(self, "buyScience"):
            self.buyScience.destroy()

        self.choixTemporaire = event.widget.cget("text")

        self.buyScience = tk.Frame(self, bg=hexDarkGrey,
                                   highlightbackground=hexBrightYellow,
                                   highlightthickness=2)
        buyLabel = tk.Label(self.buyScience, text="Buy science?",
                            fg=hexBrightYellow, bg=hexDarkGrey,
                            font=("Arial", 10))

        self.buyScience.place(relx=0.5, rely=0.8, anchor="center")
        buyLabel.place(relx=0.06, rely=0.65)

        OuiBouton = tk.Button(self.buyScience, text="Oui", width=10,
                              height=1, bg=hexBrightGreen
                              )
        annulerBouton = tk.Button(self.buyScience, text="Annuler", width=10,
                                  height=1, bg=hexRed,
                                  command=self.buyScience.destroy
                                  )
        OuiBouton.bind("<Button-1>", self.buy_science)

        OuiBouton.grid(row=1, column=0, sticky="nsew")
        annulerBouton.grid(row=1, column=1, sticky="nsew")
        buyLabel.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Science tree")
    root.geometry("800x600")
    arbre = ArbreScience(root)
    arbre.grid(row=0, column=0, sticky="nsew")
    root.mainloop()
