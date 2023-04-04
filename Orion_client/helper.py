"""Module de geometrie 2D

Ce module contient des methodes statiques pour calculer des points
et des angles a partir de coordonnees cartesiennes.
"""
import os
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


class CommandQueue:
    def __init__(self) -> None:
        self.queue = []

    def add(self, funct_name: str, *args: Any) -> None:
        """Ajoute une commande dans la queue.
        :param funct_name: Le nom de la fonction.
        :param args: Les arguments de la fonction.
        """
        self.queue.append((funct_name, args))

    def execute(self, command_obj) -> None:
        """Execute la queue grace a l'objet en parametre."""
        for funct_name, args in self.queue:
            print(funct_name, args)
            getattr(command_obj, funct_name)(*args)
        self.queue = []

    def get_all(self) -> List[tuple[str, tuple[Any]]]:
        """Retourne la queue.
        :return: La queue.
        :rtype: list[tuple[str, str, tuple[Any]]]
        """
        temp_copy = self.queue.copy()
        self.queue.clear()
        return temp_copy


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


class MusicManager:
    def __init__(self) -> None:
        self.current_music = None
        self.music = {}
        self.played_music = []
        self.volume = 1

    def add_music(self, name: str, path: str) -> None:
        """Ajoute une musique.
        :param name: Le nom de la musique.
        :param path: Le chemin vers la musique.
        """
        self.music[name] = path

    def start_shuffle_loop(self) -> None:
        """Joue une musique au hasard en boucle."""
        self.shuffle()
        self.current_music.on_end = self.start_shuffle_loop

    def shuffle(self) -> None:
        """Joue une musique au hasard."""
        import random
        if len(self.played_music) == len(self.music):
            self.played_music = []
        self.play(random.choice(list(self.music.keys())))
        self.played_music.append(self.current_music)

    def play(self, name: str) -> None:
        """Joue une musique.
        :param name: Le nom de la musique.
        """
        if name in self.music:
            self.current_music = wave.open(self.music[name], 'rb')
            self.current_music.play()
        else:
            raise ValueError(f"La musique {name} n'existe pas.")

        if self.volume != 1:
            self.change_volume(self.volume)

    def pause(self) -> None:
        """Met en pause la musique."""
        self.current_music.pause()

    def resume(self) -> None:
        """Reprend la musique."""
        self.current_music.resume()

    def stop(self) -> None:
        """Arrête la musique."""
        self.current_music.stop()

    def change_volume(self, factor):
        # Get the parameters of the audio file
        nchannels, sampwidth, framerate, nframes,\
            comptype, compname = self.current_music.getparams()
        # Read all the frames of the audio file
        frames = self.current_music.readframes(nframes)
        # Convert the frames to a list of integers
        data = struct.unpack(f"{nframes * nchannels}s", frames)[0]
        data = list(struct.unpack(f"{nframes * nchannels}h", data))
        # Change the volume of the audio file by the given factor
        data = [int(d + factor) for d in data]
        # Move the file pointer to the beginning of the file
        self.current_music.rewind()
        # Convert the list of integers back to bytes and write to the audio file
        self.current_music.writeframes(struct.pack(f"{nframes * nchannels}h", *data))



