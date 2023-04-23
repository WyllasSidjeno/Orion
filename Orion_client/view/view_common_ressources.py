"""
Ce fichier contient les ressources communes à toutes les vues
"""
from enum import Enum

police: str = "FixedSys"


class Color(Enum):
    """Enumération des couleurs utilisées dans l'application"""
    darkGrey = "#36393f"
    dark = "#2f3136"
    spaceBlack = "#23272a"
    darkGreen = "#0A6522"
    greyGreen = "#444C38"
    yellowGreen = "#C7EA46"
    grey = "#2f3136"
    brightYellow = "#F7CE25"
    brightGreen = "#cbff00"
    red = "#ff5200"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


