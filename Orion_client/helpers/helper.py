"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
import os
import threading
from enum import Enum
import random
from typing import Any, List
import functools


from typing import TYPE_CHECKING

import wave
import struct

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


class StringTypes(Enum):
    """Classe énumérative pour retrouver les strings des types de planètes."""
    # Les éléments de maps
    ETOILE_OCCUPEE = "etoile_occupee"
    ETOILE = "etoile"
    TROUDEVERS = "TrouDeVers"

    # Les éléments de joueurs
    VAISSEAU = "vaisseau"
    MILITAIRE = "militaire"
    TRANSPORTATION = "transportation"
    RECONNAISSANCE = "reconnaissance"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    @classmethod
    def ship_types(cls) -> list[str]:
        """Retourne la liste des types de vaisseaux.
        :return: La liste des types de vaisseaux.
        :rtype: list[str]
        """
        return [cls.VAISSEAU.value, cls.MILITAIRE.value,
                cls.TRANSPORTATION.value, cls.RECONNAISSANCE.value]

    @classmethod
    def planet_types(cls) -> list[str]:
        """Retourne la liste des types de planètes.
        :return: La liste des types de planètes.
        :rtype: list[str]
        """
        return [cls.ETOILE_OCCUPEE.value, cls.ETOILE.value,
                cls.TROUDEVERS.value]


class MessageManager:
    def __init__(self):
        self.messages: list[tuple[str, str]] = []
        self.new_messages: int = 0

    def add_message(self, message):
        self.messages.append(message)
        self.new_messages += 1

    def get_new_messages(self):
        messages = self.messages[-self.new_messages:]
        self.new_messages = 0
        return messages
