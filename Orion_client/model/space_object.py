import random

from Orion_client.helpers.helper import get_prochain_id, AlwaysInt
from Orion_client.model.building import Building
from Orion_client.model.ressource import Ressource
from random import randrange


class TrouDeVers:
    """Classe representant un trou de vers.
    Un trou de vers est un lien entre deux systemes stellaires. Il
    permet de voyager d'un systeme a l'autre en passant par l'hyper-espace
    via une porte de vers vers une autre porte de vers. todo: link"""

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Constructeur de la classe TrouDeVers.
        :param x1: coordonnee x de la premiere porte de vers
        :param y1: coordonnee y de la premiere porte de vers
        :param x2: coordonnee x de la deuxieme porte de vers
        :param y2: coordonnee y de la deuxieme porte de vers
        """
        self.id = get_prochain_id()
        taille = randrange(6, 20)
        self.porte_a = PorteDeVers(self.id, x1, y1, taille)
        self.porte_b = PorteDeVers(self.id, x2, y2, taille)
        self.liste_transit = []

    def tick(self) -> None:
        """Envoie le signal de jouer_prochain_coup
        aux deux portes de vers du trou de vers."""
        self.porte_a.tick()
        self.porte_b.tick()


class PorteDeVers:
    """Classe representant une porte de vers.
    Une porte de vers est une partie d'un trou de vers. Il s'agit de
    la partie visible de l'hyper-espace. Elle est representee par un
    cercle qui se dilate et se contracte."""

    def __init__(self, hole_id: str, x: int, y: int, taille: int) -> None:
        """Constructeur de la classe PorteDeVers.
        :param parent_id: l'id du trou de vers auquel la porte de vers appartient
        :param x: coordonnee x du centre de la porte
        :param y: coordonnee y du centre de la porte
        :param couleur: la couleur de la porte
        :param taille: la taille de la porte
        """
        self.parent_id = hole_id
        self.id = get_prochain_id()
        self.x = x
        self.y = y
        self.pulsemax = taille
        self.pulse = randrange(self.pulsemax)

    def tick(self) -> None:
        """Incremente le compteur de pulsation de la porte ou le remet
        a zero si il atteint la taille maximale."""
        self.pulse += 1
        if self.pulse >= self.pulsemax:
            self.pulse = 0


class Etoile:
    """Classe representant une etoile.
    Une etoile est un objet celeste qui contient des ressources et
    potentiellement un propriétaire."""

    def __init__(self, x: int, y: int, local_queue, planet_name_csv) -> None:
        """Constructeur de la classe Etoile.
        :param parent: le modele auquel l'etoile appartient
        :param x: coordonnee x de l'etoile
        :param y: coordonnee y de l'etoile
        """
        self.local_queue = local_queue
        self.log = []
        self.transit: bool = False
        self.id: str = get_prochain_id()
        # Is a csv file with planet names
        self.name = random.choice(planet_name_csv)
        self.proprietaire: str = ""
        self.x = x
        self.y = y
        self.position = (x, y)
        self.taille = randrange(4, 8)
        self.output = Ressource(metal=random.randint(1, 10),
                                energie=0,
                                beton=random.randint(1, 10),
                                nourriture=random.randint(1, 10),
                                science=0)
        #TODO: retire le champ population du constructeur de Ressources.
        self.resistance = 100
        self.buildinglist: list[Building] = []
        self.couleur = "white"
        self.population = random.randint(100, 200)
        self.needs_refresh: bool = False
    def tick(self) -> None:
        """Envoie le signal de jouer_prochain_coup
        a l'etoile."""
        if self.needs_refresh is True:
            self.needs_refresh = False

    def attacked(self, damage: int) -> None:
        self.resistance -= damage
        if self.resistance <= 0:
            self.local_queue.add("change_planet_ownership", self.id, None,
                                 self.proprietaire)

    def to_mouse_over_dict(self) -> dict:
        """Retourne un dictionnaire contenant les informations
        necessaires pour afficher les informations de l'etoile
        dans la fenetre d'information."""
        return {"header": "Etoile",
                "name": self.name,
                "owner": self.proprietaire,
                "output": self.output,
                "population": self.population
                }