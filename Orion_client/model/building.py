""" Module représentant les modele des bâtiments construisible du jeu"""
from abc import abstractmethod, ABC

from Orion_client.model.ressource import RessourceMul, Ressource


class Building(ABC):
    """Classe représentant un bâtiment
    Cette classe contient les attributs et les méthodes communes à tous les
    bâtiments du jeu.
    :param name: le nom du bâtiment
    :param cost: le coût du bâtiment
    :param level: le niveau du bâtiment
    :param max_level: le niveau maximum du bâtiment
    :param description: la description du bâtiment
    """
    def __init__(self, name: str, description: str, upgrade_cost: Ressource,
                 output: Ressource, level: int, max_level: int,
                 consumption: int = 100):
        """Constructeur de la classe Building
        :param name: le nom du bâtiment
        :param description: la description du bâtiment
        :param upgrade_cost: le coût de l'amélioration du bâtiment
        :param output: la production du bâtiment
        :param level: le niveau du bâtiment
        :param max_level: le niveau maximum du bâtiment
        """
        # todo: Ressource class
        self.name = name
        self.description = description
        self.cost = upgrade_cost
        self.output = output
        self.level = level
        self.max_level = max_level
        self.consumption = consumption

    def __str__(self):
        return f"{self.name} (lvl {self.level})"

    @abstractmethod
    def upgrade(self):
        """Méthode permettant d'améliorer un bâtiment.
        """
        raise NotImplementedError


class Mine(Building):
    """Classe représentant une mine
    Cette classe contient les attributs et les méthodes communes à toutes les
    mines du jeu.
    """
    def __init__(self):
        name = "Mine"
        description = "Une mine de fer extractant les ressources du sol"
        upgrade_cost: Ressource = Ressource(metal=2000, beton=3000, energie=1000)
        output: RessourceMul = RessourceMul(metal=2, beton=1, energie=1, nourriture=1, population=1, science=1)
        level = 1
        max_level = 3
        consumption = 5
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une mine.
        """
        self.level += 1
        self.output = self.output * 1.5

    @staticmethod
    def build_request(ressource_joueur: Ressource, list_building: list, pos: int) -> bool:
        """Méthode permettant de savoir si le joueur peut acheter une mine.
        :return: True si le joueur peut acheter une batiment, False sinon
        """
        build_cost: Ressource = Ressource(metal=2000, beton=3000, energie=1000)/2
        can_afford = True
        for key in ressource_joueur:
            if ressource_joueur[key] <= build_cost[key]:
                can_afford = False

        if can_afford:
            ressource_joueur - build_cost
            list_building.insert(pos, Mine())

        return can_afford


class Farm(Building):
    """Classe représentant une ferme
    Cette classe contient les attributs et les méthodes communes à toutes les
    fermes du jeu.
    """
    def __init__(self):
        name = "Ferme"
        description = "Une ferme produisant de la nourriture"
        upgrade_cost: Ressource = Ressource(metal=1000, beton=1500, energie=2500)
        output: RessourceMul = RessourceMul(metal=1, beton=1, energie=1, nourriture=2, population=1, science=1)
        level = 1
        max_level = 3
        consumption = 5
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une ferme.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 1.5  # todo : Ressource

    @staticmethod
    def build_request(ressource_joueur: Ressource, list_building: list, pos: int) -> bool:
        """Méthode permettant de savoir si le joueur peut acheter une mine.
        :return: True si le joueur peut acheter une batiment, False sinon
        """
        build_cost: Ressource = Ressource(metal=1000, beton=1500, energie=2500) / 2
        can_afford = True
        for key in ressource_joueur:
            if ressource_joueur[key] <= build_cost[key]:
                can_afford = False

        if can_afford:
            ressource_joueur - build_cost
            list_building.insert(pos, Farm())

        return can_afford


class ConcreteFactory(Building):
    """Classe représentant une usine à béton
    Cette classe contient les attributs et les méthodes communes à tout les
    building du jeu.
    """
    def __init__(self):
        name = "Usine "
        description = "Une usine produisant du beton"
        upgrade_cost: Ressource = Ressource(metal=1000, beton=3000, energie=2000)
        output: RessourceMul = RessourceMul(metal=1, beton=2, energie=1, nourriture=1, population=1, science=1)

        level = 1
        max_level = 3
        consumption = 5
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une usine.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 1.5  # todo : Ressource

    @staticmethod
    def build_request(ressource_joueur: Ressource, list_building: list, pos: int) -> bool:
        """Méthode permettant de savoir si le joueur peut acheter une mine.
        :return: True si le joueur peut acheter une batiment, False sinon
        """
        build_cost: Ressource = Ressource(metal=1000, beton=3000, energie=2000) / 2
        can_afford = True
        for key in ressource_joueur:
            if ressource_joueur[key] <= build_cost[key]:
                can_afford = False

        if can_afford:
            ressource_joueur - build_cost
            list_building.insert(pos, ConcreteFactory())

        return can_afford


class PowerPlant(Building):
    """Classe représentant une centrale électrique
    Cette classe contient les attributs et les méthodes communes à toutes les
    centrales électriques du jeu.
    """

    def __init__(self):
        name = "Centrale électrique"
        description = "Une centrale électrique produisant de l'électricité"
        upgrade_cost: Ressource = Ressource(metal=4000, beton=1000, energie=1000)
        output: Ressource = Ressource(energie=100)
        level = 1
        max_level = 3
        consumption = 0
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une centrale électrique.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 2  # todo : Ressource

    @staticmethod
    def build_request(ressource_joueur: Ressource, list_building: list, pos: int) -> bool:
        """Méthode permettant de savoir si le joueur peut acheter une mine.
        :return: True si le joueur peut acheter une batiment, False sinon
        """
        build_cost: Ressource = Ressource(metal=4000, beton=1000, energie=1000) / 2
        can_afford = True
        for key in ressource_joueur:
            if ressource_joueur[key] <= build_cost[key]:
                can_afford = False

        if can_afford:
            ressource_joueur - build_cost
            list_building.insert(pos, PowerPlant())

        return can_afford


class ResearchCenter(Building): #todo Research center avec science
    """Classe représentant un centre de recherche
    Cette classe contient les attributs et les méthodes communes à tous les
    centres de recherches du jeu.
    """
    building_cost: dict = {}  # todo: Ressource class

    def __init__(self):
        """Constructeur de la classe"""
        name = "Centre de recherche"
        description = "Un centre de recherche produisant des technologies"
        upgrade_cost: dict = {}  # todo: Ressource class
        output: dict = {}  # todo: Science class
        level = 1
        max_level = 3
        consumption = 5
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer un centre de recherche.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 2

    @staticmethod
    def build_request(ressource_joueur: Ressource, list_building: list, pos: int) -> bool:
        """Méthode permettant de savoir si le joueur peut acheter une mine.
        :return: True si le joueur peut acheter une batiment, False sinon
        """
        build_cost: Ressource = Ressource(metal=4000, beton=1000, energie=1000) / 2
        can_afford = True
        for key in ressource_joueur:
            if ressource_joueur[key] <= build_cost[key]:
                can_afford = False

        if can_afford:
            ressource_joueur - build_cost
            list_building.insert(pos, ResearchCenter())

        return can_afford

