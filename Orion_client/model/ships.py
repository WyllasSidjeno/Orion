"""Module des modele des vaisseaux"""
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
        self.id: str = get_prochain_id()
        self.owner = owner
        self.pos = pos
        self.angle = angle
        self.vitesse = vitesse
        self.position_cible = position_cible
        self.direction_angle = None
        self.vie = AlwaysInt(vie)
        self.vie_max = AlwaysInt(vie)
    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.position_cible is not None:
            self.update_direction_angle()
            self.move()

    def move(self):
        """Deplace le vaisseau d'une certaine distance."""
        self.pos = (self.pos[0] + self.vitesse * cos(self.direction_angle),
                    self.pos[1] + self.vitesse * sin(self.direction_angle))

    def turn(self):
        """Tourne le vaisseau d'un certain angle."""
        pass # TODO Tourner dans le view

    def update_direction_angle(self):
        """Retourne l'angle de direction du vaisseau."""
        dx = self.position_cible[0] - self.pos[0]
        dy = self.position_cible[1] - self.pos[1]
        self.direction_angle = atan2(dy, dx)


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
        direction = None
        vie = 100
        super().__init__(pos, angle, vitesse, direction, vie, owner)
        self.attack_strength = 10
        self.defense_strength = 10

    # Return a string representation of only the name of the class
    def __repr__(self):
        return "Fighter"


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
        direction = None
        vie = 100
        super().__init__(pos, angle, vitesse, direction, vie, owner)
        self.attack_strength = 0
        self.defense_strength = 0

    def __repr__(self):
        return "Cargo"


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
        direction = None
        vie = 100
        super().__init__(pos, angle, vitesse, direction, vie, owner)
        self.attack_strength = 0
        self.defense_strength = 0

    def __repr__(self):
        return "Recon"
