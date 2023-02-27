"""Module qui contient la classe Science et Science Tree"""
import tkinter as tk
from Orion_client.helper import AlwaysInt


# from __future__ import annotations

class ArbreScience:
    """Classe qui contient l'arbre de science"""
    niveau_vaisseau_dispo = AlwaysInt(0)  # niveau de vaisseau débloqué
    niveau_batiment_dispo = AlwaysInt(0)  # niveau de bâtiment débloqué
    science_acquise = AlwaysInt(0)
    sciences: dict = {"science1", "science2", "science3"}

    def __init__(self):
        """Constructeur de la classe"""
        self.root = root

        self.science_points = AlwaysInt(0)  # points de science

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
    sciences: dict = {"science1", "science2", "science3"}

    def __init__(self, root):
        self.root = root
        self.science_points = AlwaysInt(0)  # points de science
        self.canvas = tk.Canvas(root, width=300, height=200, background='white')

    def show_science(self, sciences: dict):
        """Affiche les sciences"""
        maxColumn = AlwaysInt(3)
        maxRow = AlwaysInt(0)
        x0, y0 = 10, 10
        x1, y1 = 75, 55

        self.canvas.create_rectangle(x0, y0, x1, y1, fill="red", outline="black")
        self.canvas.create_line(x1, y1 - 20, x1 + 50, y1 - 20, fill="black")

        for i in range(maxColumn):
            self.canvas.columnconfigure(i, weight=1)
        for i, science in enumerate(sciences):
            setattr(self, f"{science}_{i}", tk.Frame(self.canvas))
            if i > maxRow:
                getattr(self, f"{science}_{i}").grid(row=maxRow+1 , column=0)
                getattr(self, f"{science}_{i}").configure(bg="red")

        self.canvas.pack()


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


if __name__ == "__main__":
    root = tk.Tk()
    root.title = "Science tree"
    controller = Controller(root)
    controller.show_science(ArbreScience.sciences)
    root.mainloop()
