import tkinter as tk
from tkinter import ttk

from mvc.gui.controllers import ConfigController, EEGController
from mvc.gui.view import ConfigView, EEGView


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

    def create_second_window(self):
        second_window = tk.Toplevel(master=self.master)
        second_window.title("MindPong")
        second_window.geometry("200x200")
        ttk.Label(second_window, text="This is a new window").pack()

        eeg_controller = EEGController()  # Create Controller
        eeg_view = EEGView(second_window)  # Create View
        eeg_controller.bind(eeg_view)  # Bind View to Controller


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Settings")

    # Set the theme initially to light mode
    root.call("source", "azure.tcl")
    root.call("set_theme", "light")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.resizable(False, False)

    app = Application(master=root)

    config_controller = ConfigController(app)
    config_view = ConfigView(root)
    config_controller.bind(config_view)

    app.mainloop()
