"""Module qui contient la classe Science et Science Tree"""

# from __future__ import annotations
if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    frame = CustomFrame(root)
    frame.pack()
    root.mainloop()

    class ScienceTree:
        # AlwaysInt unlocked_ship_tier, unlocked_building_tier, acquired_science <- global
        def __init__(self):
            """Constructeur de la classe"""
            self.root = Tk()
            self.sciences = ["", "", ""] # trouver des exemples de sciences
            # toutes les sciences dispo

       # def show_science:
            # fenetre science & self.science

        # def on_click_select:

        # def is_unlockable: