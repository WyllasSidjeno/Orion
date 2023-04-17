from abc import ABC
from typing import Any, List

from Orion_client.interface import IModel, IJoueur, IController


class CommandQueue(ABC):
    def __init__(self) -> None:
        self.commands = []

    def _add(self, funct_name: str, *args: Any) -> None:
        """Ajoute une commande dans la queue.
        :param funct_name: Le nom de la fonction.
        :param args: Les arguments de la fonction.
        """
        self.commands.append((funct_name, args))

    def get(self) -> tuple[str, tuple[Any]]:
        """Retourne la prochaine commande.
        :return: La prochaine commande.
        :rtype: tuple[str, tuple[Any]]
        """
        return self.commands.pop(0) if not self.is_empty() else None

    def is_empty(self) -> bool:
        """Retourne si la queue est vide.
        :return: Si la queue est vide.
        :rtype: bool
        """
        return len(self.commands) == 0

    def get_all(self) -> List[tuple[str, tuple[Any]]]:
        """Retourne toutes les commandes.
        :return: Toutes les commandes.
        :rtype: list[tuple[str, tuple[Any]]]
        """
        temp = self.commands
        self.commands = []
        return temp


class ModelQueue(IModel, CommandQueue):
    def change_planet_ownership(self, planet_id: str,
                                new_owner: None | str = None,
                                old_owner: None | str = None) -> None:
        """Change la propriété d'une planète.
        :param planet_id: L'id de la planète.
        :param new_owner: Le nouveau propriétaire.
        :param old_owner: L'ancien propriétaire.
        """
        self._add("change_planet_ownership", planet_id,
                   new_owner, old_owner)

    def target_change_request(self, ship_informations: dict,
                              target: dict) -> None:
        """Change la cible d'un vaisseau.
        :param ship_informations: Les informations du vaisseau.
        :param target: La nouvelle cible.
        """
        self._add("target_change_request", ship_informations, target)


class JoueurQueue(IJoueur, CommandQueue):
    def construct_ship_request(self, planet_id: str, type_ship: str) -> None:
        """Demande la construction d'un vaisseau.
        :param planet_id: L'id de la planète.
        :param type_ship: Le type de vaisseau.
        """
        self._add("construct_ship_request", planet_id, type_ship)

    def remove_ship(self, ship_id: str, ship_type: str) -> None:
        """Demande la destruction d'un vaisseau.
        :param ship_id: L'id du vaisseau.
        :param ship_type: Le type de vaisseau.
        """
        self._add("remove_ship", ship_id, ship_type)

    def construct_building_request(self, planet_id: str, type_building: str):
        """Demande la construction d'un bâtiment.
        :param planet_id: L'id de la planète.
        :param type_building: Le type de bâtiment.
        """
        self._add("construct_building_request", planet_id, type_building)


class ControllerQueue(IController, CommandQueue):
    def handle_building_construct_request(self, planet, building_type):
        self._add("handle_building_construct_request", planet, building_type)

    def handle_right_click(self, pos, new_tags_list) -> None:
        """Gère le clic droit.
        :param pos: La position du clic.
        :param new_tags_list: La liste des tags.
        """
        self._add("handle_right_click", pos, new_tags_list)

    def handle_left_click(self, pos, new_tags_list) -> None:
        """Gère le clic gauche.
        :param pos: La position du clic.
        :param new_tags_list: La liste des tags.
        """
        self._add("handle_left_click", pos, new_tags_list)

    def look_for_ship_interactions(self, tags_list: list[str],
                                   pos: tuple[int, int]):
        """Gère le clic gauche.
        :param tags_list: La liste des tags.
        :param pos: La position du clic.
        """
        self._add("look_for_ship_interactions", tags_list, pos)

    def handle_ship_construct_request(self, *args):
        """Gère la demande de construction d'un vaisseau.
        :param args: Les arguments.
        """
        self._add("handle_ship_construct_request", *args)


