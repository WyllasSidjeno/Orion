"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
from typing import Any
import functools

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Orion_client.model.modele import Joueur, Modele

prochainid: int = 0
"""Prochain identifiant a utiliser."""


def get_prochain_id() -> str:
    """Recupere le prochain id a utiliser.
    # Tel que : self.__class__.prochainid += 1
    #           return f'id_{self.__class__.prochainid}'
    :return: L'ID a utiliser.
    :rtype: str
    """
    global prochainid
    prochainid += 1
    return f'id_{prochainid}'


def get_random_username() -> str:
    """Recupere un id aleatoire.
    :return: L'ID a utiliser.
    :rtype: str
    """
    import random
    return f'Joueur_{random.randint(0, 1000)}'


class Inherited(type):
    """Permet de reféfinir des méthodes héritées afin que le type de
    retour soit celui de la sous-classe.
    """

    def __new__(
            cls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any]
    ):

        implemented: dict[type, list[str]] = namespace['_implements']

        for base, methods in implemented.items():
            for method_name in methods:
                # Force early binding
                def outer(method_name=method_name):
                    method = getattr(base, method_name)

                    @functools.wraps(method)
                    def inner(self, *args, **kwargs):
                        res = method.__call__(self, *args, **kwargs)
                        reflected = f"__r{method_name[2:-2]}__"

                        # Implement reflected methods
                        if (
                                res is NotImplemented
                                and len(args) == 1  # Only binary ops
                                and reflected in dir(args[0])
                        ):
                            res = getattr(args[0], reflected).__call__(self)

                        return self.__class__(res)

                    return inner

                namespace[method_name] = outer(method_name)

        return super().__new__(cls, name, bases, namespace)


class AlwaysInt(int, metaclass=Inherited):
    _implements = {
        int: [
            '__abs__', '__invert__', '__neg__', '__pos__',
            '__ceil__', '__floor__', '__trunc__',
        ]
    }

    for method in dir(int):
        if method.startswith('__'):
            if f"__r{method[2:-2]}__" in dir(int):
                _implements[int].append(method)


def call_wrapper(target: str,
                 funct_name: str,
                 *args: Any) -> tuple[str, str, tuple[Any]]:
    """Wrapper pour les fonctions de Joueur et Modele.
    :param target: Le joueur ou le model.
    :type target: str ('nom' ou 'model')
    :param funct_name: Le nom de la fonction.
    :param add_func_name: Les noms des fonctions à ajouter.
    :param args: Les arguments de la fonction.
    """
    return target, funct_name, args

class CommandQueue:
    """Classe permettant de stocker les commandes a executer sous format
    (player, command, args) afin d'être traiter par le serveur.
    et ensuite par le modele.
    """
    def __init__(self, players: list[str], user: str):
        """Constructeur."""

        self.commands: dict[str, dict[str, list[tuple[Any]]]] = {}
        """Dictionnaire des commandes.
        """
        self.main_player: str = user
        """Le joueur principal de ce client."""

        for player in players:
            self.commands[player] = {
                "ship_target_change_request": [],
                "ship_target_to_colonize_request": [],
                "ship_target_to_attack_request": [],

                "construct_ship_request": [],

            }

        self.commands['model'] = {
            "change_planet_owner": [],
        }

    def add(self, target: str, command: str, *args: Any) -> None:
        """Ajoute une commande_queue a la liste des commandes. Les commandes sont
        executées dans l'ordre d'ajout.
        :param target: La cible. Soit un joueur, soit le model.
        :param command: Le nom de la methode a executer.
        :param args: Les arguments de methode.
        """
        if target == 'main_player':
            target = self.main_player
        self.commands[target][command].append(args)

    def get_all(self) -> list[tuple[str, str, tuple[Any]]]:
        """Recupere toutes les commandes et les supprime de la liste.
        :return: Les commandes.
        """
        commands = []
        for player in self.commands:
            for command in self.commands[player]:
                for args in self.commands[player][command]:
                    commands.append((player, command, args))
                self.commands[player][command].clear()
        return commands
    def clear(self):
        """Supprime toutes les commandes.
        """
        for player in self.commands:
            for command in self.commands[player]:
                self.commands[player][command].clear()

    def __iter__(self):
        """Fonction magique permettant d'iterer sur les commandes.

        Exemple :
        for command in self.command_queue:
            print(command)
        """
        return iter(self.commands)

    def __getitem__(self, item):
        """Fonction magique permettant d'acceder aux commandes.

        Exemple :
        self.command_queue[target][ship_target_change_request]
        """
        return self.commands[item]
