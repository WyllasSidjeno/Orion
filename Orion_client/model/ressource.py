"""Module qui contient la classe Ressource"""
from __future__ import annotations

from typing import Any

from Orion_client.helper import AlwaysInt


class Ressource(dict):
    """Classe qui contient les ressources du jeu

    Les seules ressources acceptés sont les suivantes :
        - Metal
        - Beton
        - Energie
        - Nourriture """

    def __init__(self, metal: int = 0, beton: int = 0,
                 energie: int = 0, nourriture: int = 0, **kwargs):
        """Initialise une ressource avec les valeurs par defaut à 0"""
        super().__init__(**kwargs)
        self["Metal"] = AlwaysInt(metal)
        self["Beton"] = AlwaysInt(beton)
        self["Energie"] = AlwaysInt(energie)
        self["Nourriture"] = AlwaysInt(nourriture)

    def __add__(self, other: Ressource | dict | Any) -> Ressource:
        """Additionne deux ressources"""
        if isinstance(other, dict):
            temp_ressource = Ressource()
            for key3 in other:
                if key3 in self:
                    temp_ressource[key3] = self[key3] + other[key3]
            for key2 in self:
                if key2 not in other:
                    temp_ressource[key2] = self[key2]
            return temp_ressource

        return Ressource(
            metal=self["Metal"] + other["Metal"],
            beton=self["Beton"] + other["Beton"],
            energie=self["Energie"] + other["Energie"],
            nourriture=self["Nourriture"] + other["Nourriture"]
        )

    def __sub__(self, other: Ressource | dict | Any) -> Ressource:
        """Soustrait deux ressources"""
        if isinstance(other, dict):
            temp_ressource = Ressource()
            for key2 in other:
                if key2 in self:
                    if other[key2] != 0:
                        temp_ressource[key2] = self[key2] - other[key2]
            for key3 in self:
                if key3 not in other:
                    temp_ressource[key3] = self[key3]
            return temp_ressource
        return Ressource(
            metal=self["Metal"] - other["Metal"],
            beton=self["Beton"] - other["Beton"],
            energie=self["Energie"] - other["Energie"],
            nourriture=self["Nourriture"] - other["Nourriture"]
        )

    def __truediv__(self, other: Ressource | dict | Any) -> Ressource:
        """Divise une ressource par un entier"""
        if isinstance(other, dict):
            temp_ressource = Ressource()
            for key2 in other:
                if key2 in self:
                    if other[key2] != 0:
                        temp_ressource[key2] = self[key2] / other[key2]
            for key3 in self:
                if key3 not in other:
                    temp_ressource[key3] = self[key3]
            return temp_ressource
        return Ressource(
            metal=self["Metal"] / other,
            beton=self["Beton"] / other,
            energie=self["Energie"] / other,
            nourriture=self["Nourriture"] / other
        )

    def __mul__(self, other: Ressource | dict | Any) -> Ressource:
        """Multiplie une ressource par un entier"""

        if isinstance(other, dict):
            temp_ressource = Ressource()
            for key2 in other:
                if key2 in self:
                    if other[key2] != 0:
                        temp_ressource[key2] = self[key2] * other[key2]
            for key3 in self:
                if key3 not in other:
                    temp_ressource[key3] = self[key3]
            return temp_ressource

        return Ressource(
            metal=self["Metal"] * other,
            beton=self["Beton"] * other,
            energie=self["Energie"] * other,
            nourriture=self["Nourriture"] * other
        )

    def __str__(self) -> str:
        """Affiche les ressources"""
        return f"Metal : {self['Metal']}," \
               f" Beton : {self['Beton']}, " \
               f"Energie : {self['Energie']}, " \
               f"Nourriture : {self['Nourriture']}"


# Main ne servant qu'à tester la classe Ressource
if __name__ == "__main__":
    """Test de la classe Ressource
    
    :return: None"""

    # Give me multiple way to create a Ressource object
    # 1
    ressource = Ressource()
    print(ressource)
    # -> Metal : 0, Beton : 0, Energie : 0, Nourriture : 0
    # 2
    ressource = Ressource(10, 20, 30, 40)
    print(ressource)
    # -> Metal : 10, Beton : 20, Energie : 30, Nourriture : 40
    # 3
    ressource = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource)
    # -> Metal : 10, Beton : 20, Energie : 30, Nourriture : 40
    # 4
    ressource = Ressource(metal=10, beton=20, energie=30, nourriture=40,
                          test=50)
    print(ressource)
    # -> Metal : 10, Beton : 20, Energie : 30, Nourriture : 40
    # 5
    ressource = Ressource(metal=10, beton=20)
    print(ressource)
    # -> Metal : 10, Beton : 20, Energie : 0, Nourriture : 0

    # Show the addition of two Ressource objects
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    ressource2 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 + ressource2)
    # -> Metal : 20, Beton : 40, Energie : 60, Nourriture : 80

    # Show the substraction of two Ressource objects
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    ressource2 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 - ressource2)
    # -> Metal : 0, Beton : 0, Energie : 0, Nourriture : 0

    # Show the division of a Ressource object by an int
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 / 2)
    # -> Metal : 5, Beton : 10, Energie : 15, Nourriture : 20

    # Show the multiplication of a Ressource object by an int
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 * 2)
    # -> Metal : 20, Beton : 40, Energie : 60, Nourriture : 80

    # Show the iterator
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    for key in ressource1:
        print(key)
        print(ressource1[key])
    # -> Metal
    # -> 10
    # -> Beton
    # -> 20
    # -> Energie
    # -> 30
    # -> Nourriture
    # -> 40

    # Show the .items() method
    ritem = ressource1.items()
    print(ritem)
    for key, value in ritem:
        print(key, value)
    # -> Metal 10
    # -> Beton 20
    # -> Energie 30
    # -> Nourriture 40

    print(ressource1)

    # Show the multiplication of a Ressource object by a dict
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    ressource2 = {"Metal": 2, "Beton": 3}
    print(ressource2)

    print(ressource1 * ressource2)
