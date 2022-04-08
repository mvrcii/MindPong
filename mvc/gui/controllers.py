from abc import ABC, abstractmethod

from mvc.gui.view import Config
from mvc.gui.view import View


class Controller(ABC):
    @abstractmethod
    def bind(self, view: View):
        raise NotImplementedError


class ConfigController(Controller):
    def __init__(self) -> None:
        self.view = None
        self.neighbourhoods = [
            "Entrepôt",
            "Hôtel-de-Ville",
            "Opéra",
            "Ménilmontant",
            "Louvre"
        ]
        self.room_types = [
            "Entire home/apt" "Private room",
            "Shared room",
            "Hotel room",
        ]
        self.entries_values = {}

    def bind(self, view: Config):
        self.view = view
        self.view.create_view(self.neighbourhoods, self.room_types)
        # self.view.buttons["Valider"].configure(command=self.predict)
