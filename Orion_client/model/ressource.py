"""Module qui contient la classe Ressource"""
from __future__ import annotations

from typing import Any

from Orion_client.Helpers.helper import AlwaysInt


class Ressource(dict):
    """Classe qui contient les ressources du jeu
    Les seules ressources acceptés sont les suivantes :
        - metal
        - beton
        - energie
        - nourriture """

    def __init__(self, metal: int = 0, beton: int = 0,
                 energie: int = 0, nourriture: int = 0, population: int = 0, science: int = 0, **kwargs):
        """Initialise une ressource avec les valeurs par defaut à 0"""
        super().__init__(**kwargs)
        self["metal"] = AlwaysInt(metal)
        self["beton"] = AlwaysInt(beton)
        self["energie"] = AlwaysInt(energie)
        self["nourriture"] = AlwaysInt(nourriture)
        self["population"] = AlwaysInt(population)
        self["science"] = AlwaysInt(science)

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
            metal=self["metal"] + other["metal"],
            beton=self["beton"] + other["beton"],
            energie=self["energie"] + other["energie"],
            nourriture=self["nourriture"] + other["nourriture"],
            population=self["population"] + other["population"],
            science=self["science"] + other["science"]
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
            metal=self["metal"] - other["metal"],
            beton=self["beton"] - other["beton"],
            energie=self["energie"] - other["energie"],
            nourriture=self["nourriture"] - other["nourriture"],
            population=self["population"] - other["population"],
            science=self["science"] - other["science"]
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
            metal=self["metal"] / other,
            beton=self["beton"] / other,
            energie=self["energie"] / other,
            nourriture=self["nourriture"] / other,
            population=self["population"] / other,
            science=self["science"] / other
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
            metal=self["metal"] * other,
            beton=self["beton"] * other,
            energie=self["energie"] * other,
            nourriture=self["nourriture"] * other,
            population=self["population"] * other,
            science=self["science"] * other
        )

    def __str__(self) -> str:
        """Affiche les ressources"""
        return f"metal : {self['metal']}, " \
               f"beton : {self['beton']}, " \
               f"energie : {self['energie']}, " \
               f"nourriture : {self['nourriture']}, " \
               f"population : {self['population']}, " \
               f"science : {self['science']}"

    def __dict__(self) -> dict:
        """Retourne un dictionnaire de la ressource"""
        return self


class RessourceMul(Ressource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Main ne servant qu'à tester la classe Ressource
if __name__ == "__main__":
    """Test de la classe Ressource
    
    :return: None"""

    # Give me multiple way to create a Ressource object
    # 1
    ressource = Ressource()
    print(ressource)
    # -> metal : 0, beton : 0, energie : 0, nourriture : 0
    # 2
    ressource = Ressource(10, 20, 30, 40)
    print(ressource)
    # -> metal : 10, beton : 20, energie : 30, nourriture : 40
    # 3
    ressource = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource)
    # -> metal : 10, beton : 20, energie : 30, nourriture : 40
    # 4
    ressource = Ressource(metal=10, beton=20, energie=30, nourriture=40,
                          test=50)
    print(ressource)
    # -> metal : 10, beton : 20, energie : 30, nourriture : 40
    # 5
    ressource = Ressource(metal=10, beton=20)
    print(ressource)
    # -> metal : 10, beton : 20, energie : 0, nourriture : 0

    # Show the addition of two Ressource objects
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    ressource2 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 + ressource2)
    # -> metal : 20, beton : 40, energie : 60, nourriture : 80

    # Show the substraction of two Ressource objects
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    ressource2 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 - ressource2)
    # -> metal : 0, beton : 0, energie : 0, nourriture : 0

    # Show the division of a Ressource object by an int
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 / 2)
    # -> metal : 5, beton : 10, energie : 15, nourriture : 20

    # Show the multiplication of a Ressource object by an int
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    print(ressource1 * 2)
    # -> metal : 20, beton : 40, energie : 60, nourriture : 80

    # Show the iterator
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    for key in ressource1:
        print(key)
        print(ressource1[key])
    # -> metal
    # -> 10
    # -> beton
    # -> 20
    # -> energie
    # -> 30
    # -> nourriture
    # -> 40

    # Show the .items() method
    ritem = ressource1.items()
    print(ritem)
    for key, value in ritem:
        print(key, value)
    # -> metal 10
    # -> beton 20
    # -> energie 30
    # -> nourriture 40

    print(ressource1)

    # Show the multiplication of a Ressource object by a dict
    ressource1 = Ressource(metal=10, beton=20, energie=30, nourriture=40)
    ressource2 = {"metal": 2, "beton": 3}
    print(ressource2)

    print(ressource1 * ressource2)