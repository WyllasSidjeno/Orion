"""Module des modele des vaisseaux"""
import math
from abc import ABC

from Orion_client.helper import get_prochain_id, AlwaysInt

from math import atan2, sin, cos


class Ship(ABC):
    """La classe mère de tout les vaisseaux. Elle contient les
    attributs et les méthodes communes à tout les vaisseaux.

    :ivar id: L'id du vaisseau.
    :ivar proprietaire: Le proprietaire du vaisseau.
    :ivar vitesse: La vitesse du vaisseau.
    :ivar vie: La vie du vaisseau.
    :ivar vie_max: La vie maximale du vaisseau.

    :ivar controller_model_queue: La queue du modele du controleur.
    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.
    :ivar cible_owner: Le proprietaire de la cible du vaisseau.

    :ivar id_cible: L'id de la cible du vaisseau.
    :ivar type_cible: Le type de la cible du vaisseau.

    :param pos: La position du vaisseau.
    :param vitesse: La vitesse du vaisseau.
    :param vie: La vie du vaisseau.
    :param owner: Le proprietaire du vaisseau.
    """
    id_cible: str | None
    type_cible: str | None

    def __init__(self, controller_model_queue,
                 pos: tuple, vitesse: int,
                 vie: int, owner: str, attack_strength: int = 0,
                 defense_strength: int = 0, attack_range: int = 0,):
        """Initialise un vaisseau.
        :param pos: Position du vaisseau
        :param vitesse: Vitesse du vaisseau
        :param vie: Vie du vaisseau
        :param owner: Proprietaire du vaisseau
        """
        self.id: str = get_prochain_id()
        self.proprietaire: str = owner
        self.vitesse = vitesse
        self.vie: AlwaysInt = AlwaysInt(vie)
        self.vie_max: AlwaysInt = AlwaysInt(vie)
        self.attack_strength: int = attack_strength
        self.defense_strength: int = defense_strength
        self.attack_range: int = attack_range

        self.controller_model_queue = controller_model_queue

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.vie == 0:
            self.die()
        if self.position_cible is not None:
            self.move()
            if self.position == self.position_cible:
                self.position_cible = None
        self.nouveau: bool = True

        self.position: tuple = pos
        self.angle = 0  # TODO : Type
        self.position_cible: tuple | None = None
        self.direction_angle = 0  # TODO: Type
        self.cible_owner: str | None = None

    def move(self, *args) -> None:
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

    def die(self):
        pass
        #TODO : log.add(self.owner, "ship_destruct", self.id)
        if self.position == self.position_cible:
            self.target_change(None)

    def attacked(self, attackee, attacker_info) -> None:
        """Fait subir des degats au vaisseau.
        :param damage: Les degats a subir.
        """
        print("attacked")
        damage = attacker_info[1]
        damage -= self.defense_strength
        self.vie -= damage
        print(damage)
        print(self.vie)

        if self.vie <= 0:
            self.controller_model_queue.add(
                "handle_model_to_server_queue",
                "lose_ship_request", "model", (self.id, self.proprietaire)
            )


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

    def is_static(self) -> bool:
        """Retourne True si le vaisseau est immobile."""
        return self.position_cible is None

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        if self.position_cible is not None:
            self.move()

    def type(self) -> str:
        """Retourne le type du vaisseau (le nom de sa classe)."""
        return self.__class__.__name__.lower()


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
    :ivar vie: La vie du vaisseau.
    :ivar vie_max: La vie maximale du vaisseau.

    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.
    :ivar cible_owner: Le proprietaire de la cible du vaisseau.

    :ivar id_cible: L'id de la cible du vaisseau.
    :ivar type_cible: Le type de la cible du vaisseau.

    :param pos: La position du vaisseau.
    :param owner: Le proprietaire du vaisseau.

    """

    def __init__(self, pos: tuple, owner: str,
                 model_controller_queue) -> None:
        """Initialise un vaisseau militaire.
        :param pos: Position du vaisseau
        :param owner: Proprietaire du vaisseau"""
        super().__init__(model_controller_queue,
                         pos=pos, vitesse=150, vie=100, owner=owner,
                         attack_strength=30, defense_strength=10,
                         attack_range=20)
        self.is_currently_attacking = False
        self.is_set_to_attack = False
        self.cadence = 72
        self.current_recharge = 36

    def attack(self) -> None:
        """Fait attaquer le vaisseau."""
        attacker_info = (self.id, self.type(), self.proprietaire,
                         self.attack_strength)

        enemy_info = (self.id_cible, self.type_cible, self.cible_owner)

        self.controller_model_queue.add(
            "handle_model_to_server_queue",
            "attack_request", "model", *(attacker_info, enemy_info))

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
        if new_target_type == "vaisseau" \
                or new_target_type == "etoile_occupee":
            self.is_set_to_attack = True
        else:
            self.is_set_to_attack = False

    def is_close_enough_to_attack(self,
                                  target_pos: tuple[int, int] | tuple[
                                      float, float]) -> bool:
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

    def tick(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        self.is_currently_attacking = False
        if self.current_recharge < self.cadence:
            self.current_recharge += 1

        if self.position_cible is not None:
            if self.is_close_enough_to_attack(self.position_cible) \
                    and self.is_set_to_attack:
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
    :ivar vie: La vie du vaisseau.
    :ivar vie_max: La vie maximale du vaisseau.

    :ivar log: Le log du vaisseau.
    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.
    :ivar cible_owner: Le proprietaire de la cible du vaisseau.

    :ivar id_cible: L'id de la cible du vaisseau.
    :ivar type_cible: Le type de la cible du vaisseau.
    """

    def __init__(self, pos: tuple, owner: str,
                 model_controller_queue):
        """Initialise un vaisseau de transport."""
        super().__init__(model_controller_queue,
                         pos=pos, vitesse=3, vie=100, owner=owner)

    def move(self) -> None:
        """Fait avancer le vaisseau d'une unite de temps."""
        super().move()
        if self.position == self.position_cible:
            self.target_change(None)
            # do go back after moving to target


class Reconnaissance(Ship):
    """Classe représentant un vaisseau de reconnaissance.

    :ivar id: L'id du vaisseau.
    :ivar proprietaire: Le proprietaire du vaisseau.
    :ivar vitesse: La vitesse du vaisseau.
    :ivar vie: La vie du vaisseau.
    :ivar vie_max: La vie maximale du vaisseau.

    :ivar log: Le log du vaisseau.
    :ivar nouveau: Si le vaisseau est nouveau.

    :ivar position: La position du vaisseau.
    :ivar angle: L'angle du vaisseau.
    :ivar position_cible: La position cible du vaisseau.
    :ivar direction_angle: L'angle de direction du vaisseau.
    :ivar cible_owner: Le proprietaire de la cible du vaisseau.

    :ivar id_cible: L'id de la cible du vaisseau.
    :ivar type_cible: Le type de la cible du vaisseau.
    """
    planet_id: int
    planet_owner: str
    def __init__(self, pos: tuple, owner: str):
        """Initialise un vaisseau de reconnaissance."""
        angle = 0
        vitesse = 3
        position_cible = None
        vie = 100
        super().__init__(pos, angle, vitesse, position_cible, vie, owner)
        self.attack_strength = 0  # TODO : Make this part of the mother class
        self.defense_strength = 0

    def __init__(self, pos: tuple, owner: str,
                 model_controller_queue):
        """Initialise un vaisseau de reconnaissance."""
        super().__init__(model_controller_queue,
                         pos=pos, vitesse=3, vie=100, owner=owner)

    def move(self, planet_id, proprietaire) -> None:
        """Fait avancer le vaisseau d'une unite de temps et colonise
        la planète si celle-ci est vide"""
        super().move()
        if planet_id:
            self.planet_id = planet_id
        if proprietaire:
            self.planet_owner = proprietaire

        if self.position == self.position_cible:
            self.target_change(None)
            # do colonize on arrival


class Flotte(dict):
    """Classe representant une flotte.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["militaire"]: dict[str, Militaire] = {}
        self["transportation"]: dict[str, Militaire] = {}
        self["reconnaissance"]: dict[str, Militaire] = {}
