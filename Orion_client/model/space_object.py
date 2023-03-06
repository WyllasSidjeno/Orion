import random
from random import randrange

from Orion_client.helper import get_prochain_id
from Orion_client.model.building import Building, PowerPlant, ConcreteFactory
from Orion_client.model.ressource import Ressource
from Orion_client.model.modele import Population


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
        self.porte_a = PorteDeVers(self.id, x1, y1, "red", taille)
        self.porte_b = PorteDeVers(self.id, x2, y2, "orange", taille)
        self.liste_transit = []  # pour mettre les vaisseaux qui ne sont plus dans l'espace mais maintenant l'hyper-espace

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

    def __init__(self, hole_id: str, x: int, y: int,
                 couleur: str, taille: int) -> None:
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
        self.couleur = couleur

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

    def __init__(self, parent, x: int, y: int) -> None:
        """Constructeur de la classe Etoile.

        :param parent: le modele auquel l'etoile appartient
        :param x: coordonnee x de l'etoile
        :param y: coordonnee y de l'etoile
        """
        self.transit: bool = False
        self.id: str = get_prochain_id()
        self.parent = parent
        self.proprietaire: str = ""
        self.x = x
        self.y = y
        self.position = (x, y)
        self.taille = randrange(4, 8)
        self.output = Ressource(metal=random.randint(0, 1000),
                                energie=1,
                                beton=random.randint(0, 1000),
                                nourriture=random.randint(0, 1000))
        self.buildinglist: list[Building] = [PowerPlant(), ConcreteFactory()]
        self.ressources = {"metal": 1000,
                           "energie": 10000,
                           "existentielle": 100}
        self.population = Population(5000, 1000, 1) #Paramètres (nb humain, bouffe départ, pourcentage bonus)

    def tick(self) -> None:
        """Envoie le signal de jouer_prochain_coup
        a l'etoile."""
        pass
