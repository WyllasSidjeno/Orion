from random import randrange

from Orion_client.helper import get_prochain_id


class Wormhole:
    """Classe representant un trou de vers.

    Un trou de vers est un lien entre deux systemes stellaires. Il
    permet de voyager d'un systeme a l'autre en passant par l'hyper-espace
    via une porte de vers vers une autre porte de vers. todo: link"""

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Constructeur de la classe Wormhole.

        :param x1: coordonnee x de la premiere porte de vers
        :param y1: coordonnee y de la premiere porte de vers
        :param x2: coordonnee x de la deuxieme porte de vers
        :param y2: coordonnee y de la deuxieme porte de vers
        """
        self.id = get_prochain_id()
        taille = randrange(6, 20)
        self.porte_a = Wormdoor(self, x1, y1, "red", taille)
        self.porte_b = Wormdoor(self, x2, y2, "orange", taille)
        self.liste_transit = []  # pour mettre les vaisseaux qui ne sont plus dans l'espace mais maintenant l'hyper-espace

    def jouer_prochain_coup(self) -> None:
        """Envoie le signal de jouer_prochain_coup
        aux deux portes de vers du trou de vers."""
        self.porte_a.jouer_prochain_coup()
        self.porte_b.jouer_prochain_coup()


class Wormdoor:
    """Classe representant une porte de vers.

    Une porte de vers est une partie d'un trou de vers. Il s'agit de
    la partie visible de l'hyper-espace. Elle est representee par un
    cercle qui se dilate et se contracte."""

    def __init__(self, parent: Wormhole, x: int, y: int,
                 couleur: str, taille: int) -> None:
        """Constructeur de la classe Wormdoor. todo : link

        :param parent: le trou de vers auquel la porte appartient
        :param x: coordonnee x du centre de la porte
        :param y: coordonnee y du centre de la porte
        :param couleur: la couleur de la porte
        :param taille: la taille de la porte
        """
        self.parent = parent
        self.id = get_prochain_id()
        self.x = x
        self.y = y
        self.pulsemax = taille
        self.pulse = randrange(self.pulsemax)
        self.couleur = couleur

    def jouer_prochain_coup(self) -> None:
        """Incremente le compteur de pulsation de la porte ou le remet
        a zero si il atteint la taille maximale."""
        self.pulse += 1
        if self.pulse >= self.pulsemax:
            self.pulse = 0


class Star:
    """Classe representant une etoile.

    Une etoile est un objet celeste qui contient des ressources et
    potentiellement un propriétaire."""

    def __init__(self, parent, x: int, y: int) -> None:
        """Constructeur de la classe Star.

        :param parent: le modele auquel l'etoile appartient
        :param x: coordonnee x de l'etoile
        :param y: coordonnee y de l'etoile
        """
        self.id: str = get_prochain_id()
        self.parent = parent
        self.proprietaire: str = ""
        self.x = x
        self.y = y
        self.taille = randrange(4, 8)
        self.ressources = {"metal": 1000,
                           "energie": 10000,
                           "existentielle": 100}