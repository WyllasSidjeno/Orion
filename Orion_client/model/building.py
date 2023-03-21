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
    building_cost: dict = {}  # todo: Ressource class
    baseMul = 2

    def __init__(self, name: str, description: str, upgrade_cost: dict,
                 output: RessourceMul, level: int, max_level: int, consumption: int):
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
        self.consumption = 100

    def __str__(self):
        return f"{self.name} (lvl {self.level})"

    # Abstract method that must be implemented in subclasses called upgrade
    @abstractmethod
    def upgrade(self):
        """Méthode permettant d'améliorer un bâtiment"""
        raise NotImplementedError("Subclasses must implement upgrade method")

    @staticmethod
    def can_build(ressources: dict) -> bool:  # todo : Ressource
        """Méthode statique permettant de savoir si le joueur peut construire
        une mine.
        :return: True si le joueur peut construire une batiment, False sinon
        """
        # todo : compare ressource ??

    def can_afford(self, ressources: dict) -> bool: # todo : Ressource
        """Méthode permettant de savoir si le joueur peut acheter une mine.
        :return: True si le joueur peut acheter une batiment, False sinon
        """
        # todo : compare ressource ??


class Mine(Building):
    """Classe représentant une mine
    Cette classe contient les attributs et les méthodes communes à toutes les
    mines du jeu.
    """
    building_cost: dict = {}  # todo: Ressource class


    def __init__(self):
        name = "Mine"
        description = "Une mine de fer extractant les ressources du sol"
        upgrade_cost: dict = {}  # todo: Ressource class
        output: RessourceMul = RessourceMul(metal=super().baseMul, beton=1, energie=1, nourriture=1, population=1, science=1)
        level = 1
        max_level = 3
        consumption = 100
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une mine.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 1.5 # todo : Ressource


class Farm(Building):
    """Classe représentant une ferme
    Cette classe contient les attributs et les méthodes communes à toutes les
    fermes du jeu.
    """
    building_cost: dict = {}  # todo: Ressource class

    def __init__(self):
        name = "Ferme"
        description = "Une ferme produisant de la nourriture"
        upgrade_cost: dict = {}  # todo: Ressource class
        output: RessourceMul = RessourceMul(metal=1, beton=1, energie=1, nourriture=super().baseMul, population=1, science=1)
        level = 1
        max_level = 3
        consumption = 100
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une ferme.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 1.5  # todo : Ressource


class ConcreteFactory(Building):
    """Classe représentant une usine à béton
    Cette classe contient les attributs et les méthodes communes à tout les
    building du jeu.
    """
    building_cost: dict = {}  # todo: Ressource class

    def __init__(self):
        name = "Usine "
        description = "Une usine produisant du beton"
        upgrade_cost: dict = {}  # todo: Ressource class
        output: RessourceMul = RessourceMul(metal=1, beton=super().baseMul, energie=1, nourriture=1, population=1, science=1)
        level = 1
        max_level = 3
        consumption = 100
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer une usine.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 1.5  # todo : Ressource


class PowerPlant(Building):
    """Classe représentant une centrale électrique
    Cette classe contient les attributs et les méthodes communes à toutes les
    centrales électriques du jeu.
    """
    building_cost: dict = {}  # todo: Ressource class

    def __init__(self):
        name = "Centrale électrique"
        description = "Une centrale électrique produisant de l'électricité"
        upgrade_cost: dict = {}
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
        consumption = 100
        super().__init__(name, description, upgrade_cost, output,
                         level, max_level, consumption)

    def upgrade(self):
        """Méthode permettant d'améliorer un centre de recherche.
        """
        self.level += 1
        # todo : update ressource
        self.output = self.output * 2