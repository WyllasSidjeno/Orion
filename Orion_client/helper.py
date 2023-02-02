"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
import math


class Helper(object):
    """Classe de geometrie 2D

    Cette classe contient des methodes statiques pour calculer des points
    et des angles a partir de coordonnees cartesiennes."""
    def getAngledPoint(angle: float, longueur: float, cx: float,
                       cy: float) -> tuple:
        """Calcule un point a partir d'un angle et d'une longueur

        :param angle: l'angle en radians
        :param longueur: la longueur du segment
        :param cx: coordonnee x du centre
        :param cy: coordonnee y du centre

        :return: le point calcule
        :rtype: tuple"""

        x = (math.cos(angle) * longueur) + cx
        y = (math.sin(angle) * longueur) + cy
        return (x, y)

    getAngledPoint = staticmethod(getAngledPoint)
    # permet d'appeler la methode sans instancier la classe (methode statique)

    def calcAngle(x1: int, y1: int, x2: int, y2: int) -> float:
        """Calcule l'angle entre deux points

        :param x1: coordonnee x du premier point
        :param y1: coordonnee y du premier point
        :param x2: coordonnee x du deuxieme point
        :param y2: coordonnee y du deuxieme point

        :return: l'angle en radians
        :rtype: float"""

        dx = x2 - x1
        dy = y2 - y1
        angle: float = (math.atan2(dy, dx))
        return angle

    calcAngle = staticmethod(calcAngle)

    def calcDistance(x1: int, y1: int, x2: int, y2: int) -> float:
        """Calcule la distance entre deux points en utilisant
        le theoreme de Pythagore

        :arg x1: coordonnee x du premier point
        :param y1: coordonnee y du premier point
        :param x2: coordonnee x du deuxieme point
        :param y2: coordonnee y du deuxieme point

        :return: la distance entre les deux points
        :rtype: float"""

        dx = abs(x2 - x1) ** 2
        dy = abs(y2 - y1) ** 2
        distance = math.sqrt(dx + dy)
        return distance

    calcDistance = staticmethod(calcDistance)
