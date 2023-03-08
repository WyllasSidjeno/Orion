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


class LogHelper(list):
    """Helper pour les logs de view et de modele avant envoi au serveur ou local
    """

    def __init__(self):
        super().__init__()

    def add(self, target: str, funct_name: str, *args: Any) -> None:
        """Ajoute une action.
        :param target: Le joueur ou le model.
        :type target: str ('nom' ou 'model')
        :param funct_name: Le nom de la fonction.
        :param add_func_name: Les noms des fonctions à ajouter.
        :param args: Les arguments de la fonction.
        """
        self.append((target, funct_name, args))

    def add_log(self, log) -> None:
        """Ajoute un log.
        :param log: Le log.
        """
        self.append(log)

    def get_and_clear(self):
        """Recupere les logs et supprime ses propres logs.
        :return: Les logs.
        :rtype: dict[str, list[list[str | list[Any] | tuple[Any]]]]
        """
        log = self.copy()
        self.clear()
        print(log)
        return log

    def change_main_players(self, username) -> None:
        """Change les mentions de "main_player" par "nom".
        :param username: Le nouveau nom.
        """
        for i, log in enumerate(self):
            if log[0] == 'main_player':
                self[i] = (username, *log[1:])


class Commande:
    """Classe de base pour les commandes.
    """

    def __init__(self, players: list[str]):
        # A command dictionnary that contains all of the allowed commands and accept arguments

        self.commands: dict[str, dict[str, list[tuple[Any]]]] = {}
        """Dictionnaire des commandes.
        """
        self.main_player: str = players[0]

        for player in players:
            self.commands[player] = {
                "move_ship_request": [],
                "move_ship_to_colonize_request": [],
                "move_ship_to_attack_request": [],

            }

        self.commands['model'] = {
            "change_planet_owner": [],
        }

    def add_command(self, player: str, command: str, *args: Any) -> None:
        """Ajoute une commande a la liste des commandes. Les commandes sont
        executées dans l'ordre d'ajout.
        :param player: Le joueur.
        :param command: La commande.
        :param args: Les arguments de la commande.
        """
        if player == 'main_player':
            player = self.main_player
        self.commands[player][command].append(args)

    def get_command(self, player: str,
                    command_name: str) -> tuple[str, str, tuple[Any]]:
        """Recupere une commande et ses arguments et la supprime de la liste.
        :param player: Le joueur.
        :param command_name: La commande.
        :return: Les arguments de la commande.
        """
        return player, command_name, self.commands[player][command_name].pop(0)

if __name__ == '__main__':
    command = Commande(["player1", "player2"])

    command.add_command("player1", "move_ship_request", 1, 2)

    print(command.get_command("player1", "move_ship_request"))

