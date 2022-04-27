import tkinter as tk
from threading import Thread

from scripts.mvc.controllers import ConfigController, GameController
from scripts.mvc.models import ConfigData
from scripts.mvc.view import ConfigView, GameView
import scripts.data.acquisition.read_data as read_data

from pathlib import Path


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Window settings
        self.title("Settings")
        self.resizable(False, False)

        # Set the theme initially to light mode
        theme_data_folder = Path("mvc")
        self.call("source", theme_data_folder / "azure.tcl")
        self.call("set_theme", "light")

        # Initialize data model
        self.__data_model = ConfigData()

        # Initialize the windows
        self.game_window = None
        self.config_window = ConfigWindow(self)

        self.__update_controllers()
        self.update()

    def __update_controllers(self):
        """
        Update Loop to update the controllers
        :return: None
        """
        self.config_window.config_controller.update()
        # self.game_window.game_controller.update()
        self.after(5, self.__update_controllers)

    def create_game_window(self):
        self.game_window = GameWindow(self)
        # Starting the thread to read data
        thread = Thread(target=read_data.init, args=[self.data_model], daemon=True)
        thread.start()

    def destroy_game_window(self):
        self.game_window.destroy()
        self.game_window = None
        # ToDo: Destroy/Stop Thread
        # ToDo: Clear the data in read_data or close and start a new read_data thread

    @property
    def data_model(self):
        return self.__data_model


class ConfigWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

        self.config_controller = ConfigController(self.master)
        self.config_view = ConfigView(master)
        self.config_controller.bind(self.config_view)


class GameWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        # Window settings
        self.title("MindPong")
        self.resizable(False, False)
        self.attributes("-fullscreen", True)

        self.game_controller = GameController(self.master)  # Create Controller
        self.game_view = GameView(self)  # Create View
        self.game_controller.bind(self.game_view)  # Bind View to Controller


if __name__ == "__main__":
    app = App()
    app.bind("<Escape>", quit)
    app.mainloop()
