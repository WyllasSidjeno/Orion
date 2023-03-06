"""Module qui contient la classe Science et Science Tree"""
import tkinter as tk
from Orion_client.helper import AlwaysInt


# from __future__ import annotations

class ArbreScience:
    """Classe qui contient l'arbre de science"""
    niveau_vaisseau_dispo = AlwaysInt(0)  # niveau de vaisseau débloqué
    niveau_batiment_dispo = AlwaysInt(0)  # niveau de bâtiment débloqué
    science_acquise = AlwaysInt(0)
    sciences: dict = {'science_0': [0, True, 4], 'science_1': [1, True, 5], 'science_2': [2, False, 8], 'science_3':
        [3, False, 9], 'science_4': [4, False, 10], 'science_5': [5, False, 11], 'science_6': [6, False, 13],
                      'science_7': [7, False, 15]}

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
    sciences: dict = {'science_0': [0, True, 4], 'science_1': [1, True, 5], 'science_2': [2, False, 8], 'science_3':
        [3, False, 9], 'science_4': [4, False, 10], 'science_5': [5, False, 11], 'science_6': [6, False, 13],
                      'science_7': [7, False, 15]}

    def __init__(self):
        self.root = root
        self.science_points = AlwaysInt(6)  # points de science
        self.sortedDict = sorted(self.sciences.items())
        self.maxColumn = AlwaysInt(0)
        self.maxRow = AlwaysInt(4)
        self.root.config(bg="#36393f")

    def show_science(self, data):
        """Affiche les sciences"""
        for i, science in enumerate(data.sciences):
            prix = data.sciences.get(science)[2]

            if self.science_bloquer(f"{science}", data):
                print(self.science_bloquer(f"{science}", data))
                con_frame = self.science_debloquer()
                lbl = tk.Label(con_frame, text=f"{science} prix : {prix}", height=5, width=15, bg="orange")
            else:
                con_frame = tk.Frame(self.root, bg="#2f3136", highlightbackground="black", highlightthickness=3)
                lbl = tk.Label(con_frame, text=f"{science} prix : {prix}", height=5, width=15, bg="#2f3136")

            if i % self.maxRow == 0 and i != 0:
                self.maxColumn += 1

            setattr(self, f"{science}_{i}", con_frame.grid(row=i % self.maxRow, column=self.maxColumn, padx=2, pady=2))
            setattr(self, f"{science}_{i}", lbl.grid(row=i % self.maxRow, column=self.maxColumn, padx=2, pady=2))

            lbl.bind("<Button-1>", self.on_click_select)
            lbl.grid(sticky='nsew')

    def science_bloquer(self, science, data):
        """Si points suffisant, niveau suffisant et is_unlockable
         : Affiche la case d'une science bloquée
         Sinon : Affiche la case d'une science débloquée"""
        # Ajouter les autres conditions ici
        if not data.sciences.get(science)[1] or data.sciences.get(science)[2] > self.science_points:
            return False
        else:
            return True

    def science_debloquer(self):
        con_frame = tk.Frame(self.root, bg="orange", highlightbackground="#F7CE25", highlightthickness=3)
        return con_frame

    def is_unlockable(self):
        """Vérifie si la science est débloquable
        si : science précédente débloquée et points de science suffisant"""
        pass

    def on_click_select(self, event):
        """Affiche une fenetre pour acheter la science
        button : acheter
        button : annuler"""
        # appeler la fonction is_unlockable et science_bloquer
        buyScience = tk.Frame(self.root, bg="#2f3136", highlightbackground="#F7CE25", highlightthickness=2)
        buyLabel = tk.Label(buyScience, text="Buy science?", fg="#F7CE25", bg="#2f3136", font=("Arial", 10))

        buyScience.place(relx=0.06, rely=0.65)
        buyLabel.place(relx=0.06, rely=0.65)

        OuiBouton = tk.Button(buyScience, text="Oui", width=10, height=1, bg="#cbff00")
        annulerBouton = tk.Button(buyScience, text="Annuler", width=10, height=1, bg="#ff5200",
                                  command=buyScience.destroy)

        OuiBouton.grid(row=1, column=0, sticky="nsew")
        annulerBouton.grid(row=1, column=1, sticky="nsew")
        buyLabel.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Science tree")
    root.geometry("800x600")
    controller = Controller()
    controller.show_science(ArbreScience)
    root.mainloop()

# class FenetreScience(tk.Frame):
#     def __init__(self, master: tk.Frame):
#         super().__init__(master)
#         self.root = root
#
#         self.root.columnconfigure(0, weight=1)
#         self.root.rowconfigure(0, weight=1)
#
#         self.nom_science = tk.Label(self.root, text="Science", bg="blue", font=("Arial", 10))
#
#         self.canvas = tk.Canvas(self.root)
#         self.canvas.grid(column=0, row=0, sticky="nsew")
#
#         self.nom_science.grid(column=0, row=0, columnspan=1)

# science_grid = tk.Frame(self.root, width=110, height=110, bg="orange")
# border = tk.Frame(self.root, background="red", padx=400, pady=400)
# # self.canvas.create_line(x1, y1 - 20, x1 + 50, y1 - 20, fill="black")
#
# if i % maxRow == 0 and i != 0:
#     maxColumn += 1
# setattr(self, f"{science}_{i}", science_grid.grid(row=i % maxRow, column=maxColumn))
# setattr(self, f"{science}_{i}", border.place(x=i*100, y=10))
