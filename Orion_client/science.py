"""Module qui contient la classe Science et Science Tree"""

# from __future__ import annotations
if __name__ == "__main__":
    from tkinter import Tk
    from Orion_client.helper import AlwaysInt
    # root = Tk()
    # frame = CustomFrame(root)
    # frame.pack()
    # root.mainloop()

    class ScienceTree:
        """Classe qui contient l'arbre de science"""
        niveau_vaisseau_dispo = AlwaysInt(0)  # niveau de vaisseau débloqué
        niveau_batiment_dispo = AlwaysInt(0)  # niveau de bâtiment débloqué
        science_acquise = AlwaysInt(0)
        sciences: dict = {}

        def __init__(self):
            """Constructeur de la classe"""
            self.root = Tk()
            self.science_points = 0 # points de science

        def show_science(self):
            """Affiche les sciences"""
            self.science_tree.pack()
            for science in self.science_tree:
                self.science_bloquer()
            # fenetre science & self.science

        def science_bloquer(self):
            """Si : Affiche la case d'une science bloquée
            Sinon : Affiche la case d'une science débloquée"""
            pass

        def science_debloquer(self):
            """Affiche la case d'une science débloquée"""
            pass

        def is_unlockable(self):
            """Vérifie si la science est débloquable
            si : science précédente débloquée et points de science suffisant"""
            pass

        def on_click_select(self):
            """Affiche une fenetre pour acheter la science"""
            pass

