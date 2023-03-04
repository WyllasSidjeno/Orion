"""Module des modele des vaisseaux"""
import math
from abc import ABC

from Orion_client.helper import get_prochain_id, AlwaysInt

from math import atan2, sin, cos


class Ship(ABC):
    """La classe mère de tout les vaisseaux. Elle contient les
    attributs et les méthodes communes à tout les vaisseaux.
    :param x: coordonnee x du vaisseau
    :param y: coordonnee y du vaisseau
    :param angle: angle du vaisseau
    :param vitesse: vitesse du vaisseau
    :param direction: direction du vaisseau"""

    def __init__(self, pos: tuple, angle: int, vitesse: int,
                 position_cible: tuple[int, int] | None,
                 vie: int, owner: str):
        self.id = get_prochain_id()
        self.owner = owner
        self.position = pos
        self.angle = angle
        self.vitesse = vitesse
        self.position_cible = position_cible
        self.direction_angle = 0
        self.vie = AlwaysInt(vie)
        self.vie_max = AlwaysInt(vie)
        self.new = True

    def is_static(self) -> bool:
        """Retourne True si le vaisseau est immobile."""
        return self.position_cible is None

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.position_cible is not None:
            self.move()
            if self.position == self.position_cible:
                self.position_cible = None

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        # If the ship has reached its target, stop moving
        if self.position_cible is None or self.position == self.position_cible:
            return
        # Calculate the distance and angle to the target
        dx = self.position_cible[0] - self.position[0]
        dy = self.position_cible[1] - self.position[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        angle = math.atan2(dy, dx)
        # Move the ship towards the target
        if dist < self.vitesse:
            self.position = self.position_cible
        else:
            self.position = (self.position[0] + self.vitesse * math.cos(angle),
                             self.position[1] + self.vitesse * math.sin(angle))

        print(self.position + self.position_cible)


class Fighter(Ship):
    """Classe representant un chasseur.
    :param x: coordonnee x du vaisseau
    :param y: coordonnee y du vaisseau
    :param angle: angle du vaisseau
    :param vitesse: vitesse du vaisseau
    :param direction: direction du vaisseau
    :param vie: vie du vaisseau
    :param owner: proprietaire du vaisseau"""

    def __init__(self, pos, owner: str):
        angle = 0
        vitesse = 2
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 10
        self.defense_strength = 10

    # Return a string representation of only the name of the class
    def __repr__(self):
        return "fighter"


class Cargo(Ship):
    """Classe representant un cargo.
    :param x: coordonnee x du vaisseau
    :param y: coordonnee y du vaisseau
    :param angle: angle du vaisseau
    :param vitesse: vitesse du vaisseau
    :param direction: direction du vaisseau
    :param vie: vie du vaisseau
    :param owner: proprietaire du vaisseau"""

    def __init__(self, pos, owner: str):
        angle = 0
        vitesse = 1
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 0
        self.defense_strength = 0

    def __repr__(self):
        return "cargo"


class Recon(Ship):
    """Classe representant un chasseur.
    :param x: coordonnee x du vaisseau
    :param y: coordonnee y du vaisseau
    :param angle: angle du vaisseau
    :param vitesse: vitesse du vaisseau
    :param direction: direction du vaisseau
    :param vie: vie du vaisseau
    :param owner: proprietaire du vaisseau"""

    def __init__(self, pos, owner: str):
        angle = 0
        vitesse = 3
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 0
        self.defense_strength = 0

    def __repr__(self):
        return "recon"
