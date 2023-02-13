"""Module qui contient la classe Ressource"""
from __future__ import annotations
from helper import AlwaysInt

class Ressource(dict):
    """Classe qui contient les ressources du jeu

    Les seules ressources acceptés sont les suivantes :
        - Metal
        - Beton
        - Energie
        - Nourriture """

    def __init__(self, metal: int = 0, beton: int = 0, energie: int = 0, nourriture: int = 0, **kwargs):
        """Initialise une ressource avec les valeurs par defaut à 0"""
        super().__init__(**kwargs)
        self["Metal"] = AlwaysInt(metal)
        self["Beton"] = AlwaysInt(beton)
        self["Energie"] = AlwaysInt(energie)
        self["Nourriture"] = AlwaysInt(nourriture)

    def __add__(self, other: Ressource | dict) -> Ressource:
        """Additionne deux ressources"""
        return Ressource(
            metal=self["Metal"] + other["Metal"],
            beton=self["Beton"] + other["Beton"],
            energie=self["Energie"] + other["Energie"],
            nourriture=self["Nourriture"] + other["Nourriture"]
        )

    def __sub__(self, other: Ressource | dict) -> Ressource:
        """Soustrait deux ressources"""
        return Ressource(
            metal=self["Metal"] - other["Metal"],
            beton=self["Beton"] - other["Beton"],
            energie=self["Energie"] - other["Energie"],
            nourriture=self["Nourriture"] - other["Nourriture"]
        )

    def __truediv__(self, other: Ressource | dict) -> Ressource:
        """Divise une ressource par un entier"""
        return Ressource(
            metal=self["Metal"] / other,
            beton=self["Beton"] / other,
            energie=self["Energie"] / other,
            nourriture=self["Nourriture"] / other
        )

    def __mul__(self, other: Ressource | dict) -> Ressource:
        """Multiplie une ressource par un entier"""
        return Ressource(
            metal=self["Metal"] * other,
            beton=self["Beton"] * other,
            energie=self["Energie"] * other,
            nourriture=self["Nourriture"] * other
        )

    def __str__(self) -> str:
        """Affiche les ressources"""
        return f"Metal : {self['Metal']}, Beton : {self['Beton']}, Energie : {self['Energie']}, Nourriture : {self['Nourriture']}"


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
    ressource = Ressource(metal=10, beton=20, energie=30, nourriture=40, test=50)
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



