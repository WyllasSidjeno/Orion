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


class BoundingBox:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __contains__(self, point: tuple[int, int]) -> bool:
        return self.x <= point[0] <= self.x + self.width and self.y <= point[
            1] <= self.y + self.height

    def update(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __tuple__(self):
        return self.x, self.y, self.width, self.height