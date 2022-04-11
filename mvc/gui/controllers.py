from abc import ABC, abstractmethod
import tkinter as tk
from mvc.gui.view import Config, EEG
from mvc.gui.view import View


class Controller(ABC):
    @abstractmethod
    def bind(self, view: View):
        raise NotImplementedError


class ConfigController(Controller):
    def __init__(self) -> None:
        self.view = None

    def bind(self, view: Config):
        self.view = view
        self.view.create_view()
        self.view.buttons["Start"].configure(command=self.start_eeg_window)

    def start_eeg_window(self):
        eeg_controller = EEGController()
        second_window = tk.Toplevel(self.view.master)
        eeg_view = EEG(second_window)
        eeg_controller.bind(eeg_view)


class EEGController(Controller):
    def __init__(self) -> None:
        self.view = None

    def bind(self, view: EEG):
        self.view = view
        self.view.create_view()

