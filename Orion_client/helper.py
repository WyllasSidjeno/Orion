"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
import math
from typing import Any
import functools

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

        :return: le point calcule"""

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

        :return: l'angle en radians"""

        dx = x2 - x1
        dy = y2 - y1
        angle: float = (math.atan2(dy, dx))
        return angle

    calcAngle = staticmethod(calcAngle)

    def calcDistance(x1: int, y1: int, x2: int, y2: int) -> float:
        """Calcule la distance entre deux points en utilisant
        le theoreme de Pythagore

        :param x1: coordonnee x du premier point
        :param y1: coordonnee y du premier point
        :param x2: coordonnee x du deuxieme point
        :param y2: coordonnee y du deuxieme point

        :return: la distance entre les deux points"""

        dx = abs(x2 - x1) ** 2
        dy = abs(y2 - y1) ** 2
        distance = math.sqrt(dx + dy)
        return distance

    calcDistance = staticmethod(calcDistance)


class Inherited(type):
    """Permet de reféfinir des méthodes héritées afin que le type de
    retour soit celui de la sous-classe.
    """
    def __new__(
            cls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any]
    ):

        implemented: dict[type, list[str]] = namespace['_implements']

        for base, methods in implemented.items():
            for method_name in methods:
                # Force early binding
                def outer(method_name=method_name):
                    method = getattr(base, method_name)
                    @functools.wraps(method)
                    def inner(self, *args, **kwargs):
                        res = method.__call__(self, *args, **kwargs)
                        reflected = f"__r{method_name[2:-2]}__"

                        # Implement reflected methods
                        if (
                                res is NotImplemented
                                and len(args) == 1 # Only binary ops
                                and reflected in dir(args[0])
                        ):
                            res = getattr(args[0], reflected).__call__(self)

                        return self.__class__(res)

                    return inner
                namespace[method_name] = outer(method_name)

        return super().__new__(cls, name, bases, namespace)


class AlwaysInt(int, metaclass=Inherited):
    _implements = {
        int: [
                '__abs__', '__invert__', '__neg__', '__pos__',
                '__ceil__', '__floor__', '__trunc__',
        ]
    }

    for method in dir(int):
        if method.startswith('__'):
            if f"__r{method[2:-2]}__" in dir(int):
                _implements[int].append(method)