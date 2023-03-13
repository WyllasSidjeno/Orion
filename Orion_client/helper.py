"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
from typing import Any, List
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


class CommandQueue:
    def __init__(self) -> None:
        self.queue = []

    def add(self, funct_name: str, *args: Any) -> None:
        """Ajoute une commande dans la queue.
        :param target: Le joueur ou le model.
        :type target: str ('nom' ou 'model')
        :param funct_name: Le nom de la fonction.
        :param add_func_name: Les noms des fonctions à ajouter.
        :param args: Les arguments de la fonction.
        """
        self.queue.append((funct_name, args))

    def execute(self, command_obj) -> None:
        """Execute la queue."""
        for funct_name, args in self.queue:
            getattr(command_obj, funct_name)(*args)
        self.queue = []

    def get_all(self) -> List[tuple[Any, Any]]:
        """Retourne la queue.
        :return: La queue.
        :rtype: list[tuple[str, str, tuple[Any]]]
        """
        command_list = []
        for funct_name, args in self.queue:
            command_list.append((funct_name, args))
        self.queue = []
        return command_list

