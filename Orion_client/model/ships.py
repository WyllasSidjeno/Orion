"""Module des modele des vaisseaux"""
import math
from abc import ABC

from Orion_client.helper import get_prochain_id, AlwaysInt

from math import atan2, sin, cos


class Ship(ABC):
    """La classe mère de tout les vaisseaux. Elle contient les
    attributs et les méthodes communes à tout les vaisseaux.
    """

    def __init__(self, pos: tuple, angle: int, vitesse: int,
                 position_cible: tuple[int, int] | None,
                 vie: int, owner: str):
        """Initialise un vaisseau.
        :param pos: Position du vaisseau
        :param angle: Angle du vaisseau
        :param vitesse: Vitesse du vaisseau
        :param position_cible: Position cible du vaisseau
        :param vie: Vie du vaisseau
        :param owner: Proprietaire du vaisseau
        """
        self.id: str = get_prochain_id()
        self.owner: str = owner
        self.position: tuple = pos
        self.angle = angle  # TODO : Type
        self.vitesse = vitesse
        self.position_cible: tuple = position_cible
        self.direction_angle = 0  # TODO: Type
        self.vie: AlwaysInt = AlwaysInt(vie)
        self.vie_max: AlwaysInt = AlwaysInt(vie)
        self.nouveau: bool = True

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
        #todo : Extend signature to ID.
        self.direction_angle = atan2(self.position_cible[1] - self.position[1],
                                     self.position_cible[0] - self.position[0])

        if math.hypot(
                self.position_cible[0] - self.position[0],
                self.position_cible[1] - self.position[1]) < self.vitesse:
            self.position = self.position_cible
        else:
            self.position = \
                (self.position[0] + self.vitesse * cos(self.direction_angle),
                 self.position[1] + self.vitesse * sin(self.direction_angle))

class Militaire(Ship):
    """Classe representant un vaisseau militaire.
    """
    def __init__(self, pos: tuple, owner: str):
        """Initialise un vaisseau militaire.
        :param pos: Position du vaisseau
        :param owner: Proprietaire du vaisseau"""
        angle = 0
        vitesse = 2
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 10
        self.defense_strength = 10

    # Return a string representation of only the name of the class
    def __repr__(self):
        """"""
        return "militaire"

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        super().move()
        if self.position == self.position_cible:
            self.position_cible = None
        # do colonize after


class Transport(Ship):
    """Classe representant un vaisseau de transport.
    """
    def __init__(self, pos: tuple, owner: str):
        """Initialise un vaisseau de transport."""
        angle = 0
        vitesse = 3
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 0
        self.defense_strength = 0

    def __repr__(self):
        return "transportation"

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        super().move()
        if self.position == self.position_cible:
            self.position_cible = None
            # do go back after moving to target


class Reconnaissance(Ship):
    """Classe représentant un vaisseau de reconnaissance.
    """
    def __init__(self, pos: tuple, owner: str):
        """Initialise un vaisseau de reconnaissance."""
        angle = 0
        vitesse = 3
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 0  # TODO : Make this part of the mother class
        self.defense_strength = 0

    def __repr__(self):
        return "reconnaissance"

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        super().move()
        if self.position == self.position_cible:
            self.position_cible = None
            # do colonize on arrival
