from abc import ABC, abstractmethod


class QueueSubjectInterface:
    def execute_commands(self, command_queue):
        while not command_queue.is_empty():
            command = command_queue.get()
            getattr(self, command[0])(*command[1])


class IModel(ABC, QueueSubjectInterface):
    @abstractmethod
    def change_planet_ownership(self, planet_id: str,
                                new_owner: None | str = None,
                                old_owner: None | str = None):
        raise NotImplementedError

    @abstractmethod
    def target_change_request(self, ship_informations: dict, target: dict):
        raise NotImplementedError


class IJoueur(ABC, QueueSubjectInterface):
    @abstractmethod
    def construct_ship_request(self, planet_id: str, type_ship: str):
        raise NotImplementedError

    @abstractmethod
    def remove_ship(self, ship_id: str, ship_type: str):
        raise NotImplementedError

    def construct_building_request(self, planet_id: str, type_building: str):
        raise NotImplementedError


class IController(ABC, QueueSubjectInterface):
    @abstractmethod
    def handle_right_click(self, pos, new_tags_list):
        raise NotImplementedError

    @abstractmethod
    def handle_left_click(self, pos, new_tags_list):
        raise NotImplementedError

    @abstractmethod
    def look_for_ship_interactions(self, tags_list: list[str],
                                   pos: tuple[int, int]):
        raise NotImplementedError

    @abstractmethod
    def handle_building_construct_request(self, planet, building_type):
        raise NotImplementedError

