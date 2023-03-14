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
    type_cible: str | None

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
        self.cible_owner: str | None = None

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

        if self.position == self.position_cible:
            self.target_change(None)

    def target_change(self, new_target_pos: tuple[int, int] | None,
                      new_target_id: str | None = None,
                      new_target_type: str | None = None,
                      new_target_owner: str | None = None) -> None:
        """Change la position cible du vaisseau.
        :param new_target_type: Le type de la nouvelle cible.
        :param new_target_id: L'id de la nouvelle cible.
        :param new_target_pos: La nouvelle position cible.
        :param new_target_owner: Le proprietaire de la nouvelle cible.
        """
        self.position_cible = new_target_pos
        self.type_cible = new_target_type
        self.id_cible = new_target_id
        self.cible_owner = new_target_owner

    def type(self) -> str:
        """Retourne le type du vaisseau (le nom de sa classe)."""
        return self.__class__.__name__.lower()
class Militaire(Ship):
    """Classe representant un vaisseau militaire.
    """

    def __init__(self, pos: tuple, owner: str):
        """Initialise un vaisseau militaire.
        :param pos: Position du vaisseau
        :param owner: Proprietaire du vaisseau"""
        super().__init__(pos=pos, angle=0, vitesse=150,
                         position_cible=None, vie=100, owner=owner)
        self.attack_strength = 10
        self.defense_strength = 10
        self.attack_range = 20
        self.is_currently_attacking = False
        self.is_set_to_attack = False

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        self.is_currently_attacking = False
        if self.position_cible is not None:
            if self.is_close_enough_to_attack(self.position_cible) \
                    and self.is_set_to_attack:
                self.attack_request()
            else:
                self.move()

    def attack_request(self) -> None:
        """Fait attaquer le vaisseau."""
        attacker_info = (self.id, self.type(), self.owner,
                         self.attack_strength)

        enemy_info = (self.id_cible, self.type_cible, self.cible_owner)

        self.log.append(("attack_request", attacker_info, enemy_info))


    def is_close_enough_to_attack(self, target_pos: tuple[int, int]) -> bool:
        """Retourne True si le vaisseau est assez proche de sa cible."""
        # If the target is close enough to attack or to move to attack
        if math.hypot(
                target_pos[0] - self.position[0],
                target_pos[1] - self.position[1]) \
                <= self.attack_range + self.vitesse:
            # if the target is not close enough to attack
            if math.hypot(
                    target_pos[0] - self.position[0],
                    target_pos[1] - self.position[1]) > self.attack_range:
                self.position_cible = \
                    (target_pos[0] - self.attack_range * cos(
                        self.direction_angle),
                     target_pos[1] - self.attack_range * sin(
                         self.direction_angle))
            return True
        return False

    def target_change(self, new_target_pos: tuple[int, int] | None,
                      new_target_id: str | None = None,
                      new_target_type: str | None = None,
                      new_target_owner: str | None = None) -> None:
        """Change la position cible du vaisseau.
        :param new_target_type: Le type de la nouvelle cible.
        :param new_target_id: L'id de la nouvelle cible.
        :param new_target_pos: La nouvelle position cible.
        :param new_target_owner: Le proprietaire de la nouvelle cible.
        """
        super().target_change(new_target_pos, new_target_id, new_target_type,
                              new_target_owner)
        if new_target_type == "vaisseau" or new_target_type == "etoile_occupee":
            self.is_set_to_attack = True
        else:
            self.is_set_to_attack = False


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


class Flotte(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["militaire"]: dict[str, Militaire] = {}
        self["transportation"]: dict[str, Militaire] = {}
        self["reconnaissance"]: dict[str, Militaire] = {}
