"""Module des modele des vaisseaux"""
import math
from abc import ABC

from Orion_client.helper import get_prochain_id, AlwaysInt

from math import atan2, sin, cos


class Ship(ABC):
    """La classe mère de tout les vaisseaux. Elle contient les
    attributs et les méthodes communes à tout les vaisseaux.
    """
    id_cible: str | None
    type_cible: str| None

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

        self.log = []

    def is_static(self) -> bool:
        """Retourne True si le vaisseau est immobile."""
        return self.position_cible is None

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.position_cible is not None:
            self.move()

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        # todo : Extend signature to ID.
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

    def target_change(self, new_target_pos: tuple[int, int] | None,
                      new_target_id: str | None = None,
                      new_target_type:str | None = None) -> None:
        """Change la position cible du vaisseau.
        :param new_target_type: Le type de la nouvelle cible.
        :param new_target_id: L'id de la nouvelle cible.
        :param new_target_pos: La nouvelle position cible.
        """
        self.position_cible = new_target_pos
        self.type_cible = new_target_type
        self.id_cible = new_target_id

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
        self.has_arrived: bool = True

    # Return a string representation of only the name of the class
    def __repr__(self):
        """"""
        return "militaire"

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.position_cible is not None:
            self.move()
            if self.position == self.position_cible:
                self.has_arrived = True
                self.log.append(("attack_request", self.id, self.type_cible, self.id_cible))

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if not self.has_arrived:
            super().move()

    def target_to_attack(self, target_id, target_type: str,
                         new_target_pos: tuple[int, int]) -> None:
        """Change la position cible du vaisseau.
        :param type_target: Le type de la nouvelle position cible.
        :param new_target: La nouvelle position cible.
        """
        if target_type == "vaisseau":
            self.target_change(new_target_pos, target_id, target_type)
            # Plus callback for pos
        elif target_type == "etoile":
            self.target_change(new_target_pos, target_id, target_type)

    def target_change(self, new_target_pos: tuple[int, int] | None,
                      new_target_id: str | None = None,
                      new_target_type:str | None = None) -> None:
        """Change la position cible du vaisseau.
        :param new_target_type: Le type de la nouvelle cible.
        :param new_target_id: L'id de la nouvelle cible.
        :param new_target_pos: La nouvelle position cible.
        """
        super().target_change(new_target_pos, new_target_id, new_target_type)
        self.has_arrived = False


class Transportation(Ship):
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
            self.target_change(None)
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

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        super().move()
        if self.position == self.position_cible:
            self.target_change(None)
            # do colonize on arrival

    def __repr__(self):
        return "reconnaissance"


class Flotte(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["militaire"]: dict[str, Militaire] = {}
        self["transportation"]: dict[str, Militaire] = {}
        self["reconnaissance"]: dict[str, Militaire] = {}



