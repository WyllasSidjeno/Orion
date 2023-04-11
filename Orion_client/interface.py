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
        pass

    @abstractmethod
    def target_change_request(self, ship_informations: dict, target: dict):
        pass


class IJoueur(ABC, QueueSubjectInterface):
    @abstractmethod
    def construct_ship_request(self, planet_id: str, type_ship: str):
        pass

    @abstractmethod
    def remove_ship(self, ship_id: str, ship_type: str):
        pass

class IController(ABC, QueueSubjectInterface):
    @abstractmethod
    def handle_right_click(self, pos, new_tags_list):
        pass

    @abstractmethod
    def handle_left_click(self, pos, new_tags_list):
        pass

    @abstractmethod
    def look_for_ship_interactions(self, tags_list: list[str],
                                   pos: tuple[int, int]):
        pass

