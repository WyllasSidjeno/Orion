"""Module qui contient la classe Hud"""
import tkinter as tk
from __future__ import annotations
from typing import Any
from helper import AlwaysInt
from ressource import Ressource

class Hud():
    def __init__(self):
        self.ressources = Ressource(metal=0, beton=0, energie=0, nourriture=0)

    def get_ressources(self, joueur):
        """ramasser et calculer le total des ressources du joueur dans un tableau"""
        self.ressources = Ressource
        #to be modified; get player and add all ressources to one;

    def show(self):
        """prendre les ressources du tableau et afficher dans le HUD (à l'écran)"""
        self.root = tk.Tk()
        self.root.title("starfighter")
        self.frame = tk.Frame(self.root, width=500, height=500, bg="#36393f")

