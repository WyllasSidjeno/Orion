"""Module des modele des vaisseaux"""
import math
from abc import ABC

from Orion_client.helpers.CommandQueues import JoueurQueue, ModelQueue
from Orion_client.helpers.helper import get_prochain_id, AlwaysInt

from math import atan2, sin, cos


class Ship(ABC):
    """La classe mère de tout les vaisseaux. Elle contient les
    attributs et les méthodes communes à tout les vaisseaux.

    :ivar id: L'id du vaisseau.
    :ivar proprietaire: Le proprietaire du vaisseau.
    :ivar vitesse: La vitesse du vaisseau.
    :ivar resistance: La resistance du vaisseau.
    :ivar resistance_max: La resistance maximale du vaisseau.

    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.

    :param pos: La position du vaisseau.
    :param vitesse: La vitesse du vaisseau.
    :param resistance: La resistance du vaisseau.
    :param owner: Le proprietaire du vaisseau.
    """

    def __init__(self, local_queue : ModelQueue, player_local_queue : JoueurQueue,
                 pos: tuple, vitesse: int,
                 resistance: int, owner: str, attack_strength: int = 0,
                 defense_strength: int = 0, attack_range: int = 0, consommation: int = 0):
        """Initialise un vaisseau.
        :param pos: Position du vaisseau
        :param vitesse: Vitesse du vaisseau
        :param resistance: resistance du vaisseau
        :param owner: Proprietaire du vaisseau
        """
        self.id: str = get_prochain_id()
        self.proprietaire: str = owner
        self.vitesse = vitesse
        self.resistance: AlwaysInt = AlwaysInt(resistance)
        self.resistance_max: AlwaysInt = AlwaysInt(resistance)
        self.attack_strength: int = attack_strength
        self.defense_strength: int = defense_strength
        self.attack_range: int = attack_range

        self.local_queue = local_queue
        self.player_local_queue = player_local_queue
        self.consommation: int = consommation
        self.nouveau: bool = True
        self.docked: bool = False
        self.position: tuple = pos
        self.angle = 0
        self.position_cible: tuple | None = None
        self.cible = None
        self.direction_angle = 0

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
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

    def attacked(self, damage) -> None:
        """Fait subir des degats au vaisseau.
        """
        damage -= self.defense_strength
        self.resistance -= damage
        if self.resistance <= 0:
            self.player_local_queue.remove_ship(self.id, self.type())

    def target_change(self, new_target_pos: tuple[int, int] | None,
                      target=None) -> None:
        """Change la position cible du vaisseau.
        :param new_target_pos: La nouvelle position cible.
        :param target: La nouvelle cible.
        """
        self.position_cible = new_target_pos
        self.cible = target

    def is_static(self) -> bool:
        """Retourne True si le vaisseau est immobile."""
        return self.position_cible is None

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.cible is not None:
            self.position_cible = self.cible.position
        if self.position_cible is not None:
            self.move()

    def type(self) -> str:
        """Retourne le type du vaisseau (le nom de sa classe)."""
        return self.__class__.__name__.lower()

    def is_close_enough(self) -> bool:
        """Retourne True si le vaisseau est assez proche de sa cible."""
        # If the target is close enough to attack or to move to attack
        if self.cible is not None:
            self.position_cible = self.cible.position

        if math.hypot(
                self.position_cible[0] - self.position[0],
                self.position_cible[1] - self.position[1]) \
                <= self.attack_range + self.vitesse:
            # if the target is not close enough to attack
            if math.hypot(
                    self.position_cible[0] - self.position[0],
                    self.position_cible[1] - self.position[1]) \
                    > self.attack_range:
                self.position_cible = \
                    (self.position_cible[0] - self.attack_range * cos(
                        self.direction_angle),
                     self.position_cible[1] - self.attack_range * sin(
                         self.direction_angle))
            return True
        return False


class Militaire(Ship):
    """Classe representant un vaisseau militaire.

    :ivar attack_strength: La force d'attaque du vaisseau.
    :ivar defense_strength: La force de defense du vaisseau.
    :ivar attack_range: La portee d'attaque du vaisseau.
    :ivar is_currently_attacking: Si le vaisseau est en train d'attaquer.
    :ivar is_set_to_attack: Si le vaisseau est en train d'attaquer.

    :ivar id: L'id du vaisseau.
    :ivar proprietaire: Le proprietaire du vaisseau.
    :ivar vitesse: La vitesse du vaisseau.
    :ivar resistance: La resistance du vaisseau.
    :ivar resistance_max: La resistance maximale du vaisseau.

    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.

    :param pos: La position du vaisseau.
    :param owner: Le proprietaire du vaisseau.

    """

    def __init__(self, pos: tuple, owner: str,
                 local_queue, player_local_queue) -> None:
        """Initialise un vaisseau militaire.
        :param pos: Position du vaisseau
        :param owner: Proprietaire du vaisseau"""
        super().__init__(local_queue, player_local_queue,
                         pos=pos, vitesse=6, resistance=100, owner=owner,
                         attack_strength=30, defense_strength=10,
                         attack_range=20, consommation=20)
        self.is_currently_attacking = False
        self.is_set_to_attack = False
        self.cadence = 36
        self.current_recharge = 36

    def attack(self) -> None:
        """Fait attaquer le vaisseau."""
        if self.cible is not None:
            self.cible.attacked(self.attack_strength)
            if self.cible.resistance <= 0:
                self.target_change(None)

    def target_change(self, pos, target=None) -> None:
        """Change la position cible du vaisseau.
        """
        super().target_change(pos, target)
        if target is not None:
            self.is_set_to_attack = True
        else:
            self.is_set_to_attack = False

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.cible is not None:
            self.position_cible = self.cible.position
        self.is_currently_attacking = False
        if self.current_recharge < self.cadence:
            self.current_recharge += 1

        if self.position_cible is not None:
            if self.is_close_enough() and self.is_set_to_attack:
                if self.cadence == self.current_recharge:
                    self.attack()
                    self.current_recharge = 0
            else:
                self.move()


class Transportation(Ship):
    """Classe representant un vaisseau de transport.

    :ivar id: L'id du vaisseau.
    :ivar proprietaire: Le proprietaire du vaisseau.
    :ivar vitesse: La vitesse du vaisseau.
    :ivar resistance: La resistance du vaisseau.
    :ivar resistance_max: La resistance maximale du vaisseau.

    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.

    """

    def __init__(self, pos: tuple, owner: str,
                 local_queue, player_local_queue) -> None:
        """Initialise un vaisseau de transport."""
        super().__init__(local_queue, player_local_queue,
                         pos=pos, vitesse=3, resistance=100, owner=owner, consommation=5)
        self.position_depart = pos
        self.position_origin = self.position_depart

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.is_close_enough():
            temp = self.position_depart
            self.position_depart = self.position_cible
            self.position_cible = temp
        else:
            super().move()

    def target_change(self, pos, target=None) -> None:
        super().target_change(pos, target)
        self.position_depart = self.position_origin


class Reconnaissance(Ship):
    """Classe représentant un vaisseau de reconnaissance.

    :ivar id: L'id du vaisseau.
    :ivar proprietaire: Le proprietaire du vaisseau.
    :ivar vitesse: La vitesse du vaisseau.
    :ivar resistance: La resistance du vaisseau.
    :ivar resistance_max: La resistance maximale du vaisseau.

    :ivar log: Le log du vaisseau.
    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.
    """

    def __init__(self, pos: tuple, owner: str,
                 local_queue, player_local_queue) -> None:
        """Initialise un vaisseau de reconnaissance."""
        super().__init__(local_queue, player_local_queue,
                         pos=pos, vitesse=3, resistance=100, owner=owner, consommation=15)

    def tick(self) -> None:
        if self.position_cible:
            if self.cible:
                if self.is_close_enough():
                    self.local_queue.change_planet_ownership(
                        self.cible.id, self.proprietaire)
                    self.target_change(None)
                else:
                    self.move()

            else:
                self.move()


class Flotte(dict):
    """Classe representant une flotte.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["militaire"]: dict[str, Militaire] = {}
        self["transportation"]: dict[str, Transportation] = {}
        self["reconnaissance"]: dict[str, Reconnaissance] = {}
