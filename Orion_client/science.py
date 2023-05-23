"""Module qui contient la classe Science et Science Tree"""
from tkinter import Frame, Label, Button, Tk
from helpers.helper import AlwaysInt
from view.view_common_ressources import *


class ArbreScience(Frame):
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

    choix_temporaire: str
    buyscience: Frame

    def __init__(self, master, **kwargs):
        """Constructeur de la classe"""
        super().__init__(master, **kwargs,
                         background=hexGrey, pady=10, padx=10)
        self.grid_propagate(True)
        self.science_points = 10

        self.title = Label(self, text="Arbre de science", bg=hexGrey,
                           fg="white", font=(police, 20))

        self.title.grid(row=0, column=0, sticky="nsew")

        self.science_frame = Frame(self, bg=hexGrey)
        self.science_frame.grid(row=1, column=0, sticky="nsew")

        self.show_science(ArbreScience.sciences)

    def show_science(self, sciences):
        """Affiche les sciences"""
        max_row = 0
        max_column = 4
        for i, science in enumerate(sciences):
            prix = sciences.get(science)[0]
            con_frame = Frame(
                self.science_frame, bg=hexGrey,
                highlightbackground="black",
                highlightthickness=3
            )

            if self.science_acquises(science, sciences):
                lbl = Label(con_frame, text=f"{science} prix : {prix}",
                            height=5, width=15, bg=hexDarkGreen)
            else:
                lbl = Label(con_frame, text=f"{science} prix : {prix}",
                            height=5, width=15, bg=hexGreyGreen)

            if self.science_achetable(science, sciences):
                lbl = Label(con_frame, text=f"{science} prix : {prix}",
                            height=5, width=15, bg=hexYellowGreen)

            if i % max_column == 0 and i != 0:
                max_row += 1

            setattr(self, f"{science}_{i}",
                    con_frame.grid(row=max_row,
                                   column=i % max_column, padx=2,
                                   pady=2))
            setattr(self, f"{science}_{i}",
                    lbl.grid(row=max_row, column=i % max_column,
                             padx=2, pady=2))

            if self.science_achetable(science, sciences):
                lbl.bind("<Button-1>", self.on_click_select)
            lbl.grid(sticky='nsew')

    @staticmethod
    def science_acquises(science: str, sciences: dict) -> bool:
        """Verifie si la science est acquise"""
        # Todo : Modele
        if sciences[science][1] == "acquise":
            return True
        return False

    def science_achetable(self, science: str, sciences: dict) -> bool:
        """Si points suffisant, niveau suffisant et is_unlockable
         : Affiche la case d'une science bloquée
         Sinon : Affiche la case d'une science débloquée"""
        # Todo : Modele
        if self.science_points >= sciences[science][0]:
            return True
        return False

    def buy_science(self, _):
        """Achete la science"""
        print(self.choix_temporaire.split(" ")[0])
        self.buyscience.destroy()

    def on_click_select(self, event):
        """Affiche une fenetre pour acheter la science
        button : acheter
        button : annuler"""
        # if buyscience is not None: destroy the last one
        if hasattr(self, "buyscience"):
            self.buyscience.destroy()

        self.choix_temporaire = event.widget.cget("text")

        self.buyscience = Frame(self, bg=hexDarkGrey,
                                highlightbackground=hexBrightYellow,
                                highlightthickness=2)
        buy_label = Label(self.buyscience, text="Buy science?",
                          fg=hexBrightYellow, bg=hexDarkGrey,
                          font=("Arial", 10))

        self.buyscience.place(relx=0.5, rely=0.8, anchor="center")
        buy_label.place(relx=0.06, rely=0.65)

        oui_bouton = Button(self.buyscience, text="Oui", width=10,
                            height=1, bg=hexBrightGreen
                            )
        annuler_bouton = Button(self.buyscience, text="Annuler", width=10,
                                height=1, bg=hexRed,
                                command=self.buyscience.destroy
                                )
        oui_bouton.bind("<Button-1>", self.buy_science)

        oui_bouton.grid(row=1, column=0, sticky="nsew")
        annuler_bouton.grid(row=1, column=1, sticky="nsew")
        buy_label.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    root = Tk()
    root.title("Science tree")
    arbre = ArbreScience(root)
    arbre.grid(row=0, column=0, sticky="nsew")
    root.mainloop()
