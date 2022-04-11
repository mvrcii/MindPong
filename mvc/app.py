import tkinter as tk
from tkinter import ttk

from mvc.gui.controllers import Controller, ConfigController
from mvc.gui.view import Config


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)


if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    app = Application(master=root)

    config_controller = ConfigController()
    config_view = Config(root)
    config_controller.bind(config_view)

    app.mainloop()
