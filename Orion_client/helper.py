"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
from typing import Any
import functools

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Orion_client.model.model import Player, Model

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
    """Wrapper pour les fonctions de Player et Model.
    :param target: Le joueur ou le model.
    :type target: str ('username' ou 'model')
    :param funct_name: Le nom de la fonction.
    :param add_func_name: Les noms des fonctions à ajouter.
    :param args: Les arguments de la fonction.
    """
    return target, funct_name, args


class LogHelper(dict):
    """Helper pour les logs de view et de modele avant envoi au serveur ou local
    """
    # Create, in the init, two categories : model and player
    def __init__(self):
        super().__init__()
        self['model'] = []
        self['player'] = []

    def add(self, target: str, funct_name: str, *args: Any) -> None:
        """Ajoute une action.
        :param target: Le joueur ou le model.
        :type target: str ('username' ou 'model')
        :param funct_name: Le nom de la fonction.
        :param add_func_name: Les noms des fonctions à ajouter.
        :param args: Les arguments de la fonction.
        """

        print(f"LogHelper.add({target}, {funct_name}, {args})")

        if target == 'model':
            self.add_model_action(funct_name, *args)
        else:
            self.add_player_action(target, funct_name, *args)

    def add_log(self, log) -> None:
        """Ajoute un log.
        :param log: Le log.
        """
        if log:
            print(f"LogHelper.add_log({log})")
            target = log[0][0]
            func_name = log[0][1]
            args = log[0][2]
            self.add(target, func_name, *args)

    def add_player_action(self, username: str, funct_name: str,
                          *args: Any) -> None:
        """Ajoute une action de joueur.
        :param player: Le joueur.
        :param funct_name: Le nom de la fonction.
        :param args: Les arguments de la fonction.
        """
        self['player'].append(call_wrapper(username, funct_name, *args))

    def add_model_action(self, funct_name: str, *args: Any) -> None:
        """Ajoute une action de model.
        :param funct_name: Le nom de la fonction.
        :param args: Les arguments de la fonction.
        """
        self['model'].append(call_wrapper('model', funct_name, *args))

    def get_and_clear(self) -> dict[list[str | list[Any] | tuple[Any]]]:
        """Recupere les logs et supprime ses propres logs.
        :return: Les logs.
        :rtype: dict[str, list[list[str | list[Any] | tuple[Any]]]]
        """
        copy = self.copy()
        self.clear()
        return copy

    def copy(self):
        """Copie les logs.
        :return: Les logs.
        """
        return self['model'].copy(), self['player'].copy()

    def clear(self) -> None:
        """Supprime les logs."""
        self['model'].clear()
        self['player'].clear()

if __name__ == '__main__':
    # Test de loghelper
    log = LogHelper()
    log.add_player_action('username', 'move_ship', 1, 2)
    log.add_model_action('add_player', 'username', 1, 2)

    print(log.get_and_clear())

    log_with_wrapper = call_wrapper('username', 'move_ship', 1, 2)
    print(log_with_wrapper)
    log_with_wrapper2 = call_wrapper('model', 'add_player', 'username', 1, 2)
    print(log_with_wrapper2)




