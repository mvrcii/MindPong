import tkinter as tk
from abc import abstractmethod
from tkinter import ttk


class View(tk.Frame):
    @abstractmethod
    def create_view(self):
        raise NotImplementedError


class Config(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.sliders = {}
        self.entries = {}
        self.buttons = {}
        self.combo_boxes = {}
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self, neighbourhoods: list, room_type: list):

        control_frame = tk.LabelFrame(master=self)
        control_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=1, column=0, sticky='nsew')

        self.create_combobox(control_frame, "Neighbourhood", row=0, column=0, values=neighbourhoods)
        self.create_combobox(control_frame, "Room type", row=0, column=1, values=room_type)

        self.create_entry(control_frame, "Subject ID", row=1, column=0, textvar=tk.IntVar())
        self.create_entry(control_frame, "Guests", row=1, column=1, textvar=tk.DoubleVar())
        self.create_entry(control_frame, "Bedrooms", row=2, column=0, textvar=tk.DoubleVar())
        self.create_entry(control_frame, "Beds", row=2, column=1, textvar=tk.DoubleVar())
        self.create_entry(control_frame, "Bath rooms", row=2, column=2, textvar=tk.DoubleVar())

        self.create_button(control_frame, "Valider", row=3, column=0)
        self.create_button(control_frame, "Start", row=3, column=1)

        self.create_slider(control_frame, "Window Size", 0, 2, 0, 10, "horizontal")
        self.create_slider(control_frame, "Window Offset", 1, 2, 0, 10, "horizontal")

    def create_slider(self, frame, label, row, column, from_, to, orientation):
        label_frame = tk.LabelFrame(frame, text=label)
        self.sliders[label] = tk.Scale(frame, from_=from_, to=to, orient=orientation)
        self.sliders[label].grid(row=row, column=column)
        frame.rowconfigure(index=row, minsize=70)
        label_frame.grid(row=row, column=column, sticky='nsew')

    def create_entry(self, frame, label, row, column, textvar):
        label_frame = tk.LabelFrame(frame, text=label)
        self.entries[label] = tk.Entry(label_frame, textvariable=textvar)
        self.entries[label].grid(row=1, column=1)
        label_frame.grid(row=row, column=column, sticky='nsew')

    def create_button(self, frame, name, row, column):
        self.buttons[name] = tk.Button(frame)
        self.buttons[name]["text"] = name
        self.buttons[name].grid(row=row, column=column, sticky='nsew')

    def create_combobox(self, frame, label, values, row, column):
        label_frame = tk.LabelFrame(frame, text=label)
        self.combo_boxes[label] = ttk.Combobox(label_frame, values=values)
        self.combo_boxes[label].grid(row=1, column=1)
        label_frame.grid(row=row, column=column, sticky='nsew')


class Graph(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self, neighbourhoods: list, room_type: list):
        control_frame = tk.Frame(master=self)
