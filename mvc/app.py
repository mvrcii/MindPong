import tkinter as tk
from mvc.gui.controllers import Controller, ConfigController
from mvc.gui.view import Config, Graph
from tkinter import ttk


class Application(ttk.Notebook):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

    def new_tab(self, controller: Controller, view: Config, name: str):
        view = view(self.master)
        controller.bind(view)
        self.add(view, text=name)


if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    app = Application(master=root)

    config_controller = ConfigController()

    app.new_tab(view=Config, controller=config_controller, name="Configuration")
    app.new_tab(view=Graph, controller=config_controller, name="Graph")

    app.mainloop()
