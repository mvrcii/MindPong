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
        self.check_boxes = {}
        self.combo_boxes = {}
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self):
        # Control Frame
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=0, column=0, sticky='nsew')

        self.create_subject(control_frame, "Subject", row=0, column=0)

        self.create_algorithm(control_frame, "Algorithm", row=1, column=0)

        self.create_slider(control_frame, "Window Size", row=4, column=0, from_=200, to=2000, interval=200,
                           orientation="horizontal")
        self.create_slider(control_frame, "Window Offset", row=5, column=0, from_=40, to=400, interval=40,
                           orientation="horizontal")
        self.create_slider(control_frame, "Trial Min-Duration", row=6, column=0, from_=800, to=1500, interval=100,
                           orientation="horizontal")

        self.create_button(control_frame, "Start", row=7, column=0)

        # Graph Frame
        graph_frame = tk.LabelFrame(master=self, text="Graph")
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.grid(padx=10, pady=5, row=0, column=1, sticky='nsew')

        self.create_checkbox(graph_frame, "C3", row=0, column=0, variable=tk.BooleanVar())
        self.create_checkbox(graph_frame, "C4", row=1, column=0, variable=tk.BooleanVar())

    def create_slider(self, frame, label, row, column, from_, to, interval, orientation):
        label_frame = tk.LabelFrame(frame, text=label)
        self.sliders[label] = tk.Scale(frame, from_=from_, to=to, tickinterval=interval, orient=orientation,
                                       resolution=interval)
        self.sliders[label].grid(padx=20, pady=20, row=row, column=column, sticky='ew')
        frame.rowconfigure(index=row, minsize=70)
        frame.columnconfigure(index=column, minsize=400)
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_subject(self, frame, label, row, column):
        label_frame = tk.LabelFrame(frame, text=label)
        self.create_entry(label_frame, "ID", row=0, column=0, text_var=tk.IntVar())
        self.create_combobox(label_frame, "Sex", ["M", "F", "D"], row=0, column=1)
        self.create_entry(label_frame, "Age", row=0, column=2, text_var=tk.IntVar())
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_algorithm(self, frame, label, row, column):
        label_frame = tk.LabelFrame(frame, text=label)
        self.create_entry(label_frame, "Threshold", row=0, column=0, text_var=tk.DoubleVar())
        self.create_entry(label_frame, "fmin", row=0, column=1, text_var=tk.DoubleVar())
        self.create_entry(label_frame, "fmax", row=0, column=2, text_var=tk.DoubleVar())
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_entry(self, frame, label, row, column, text_var):
        label_frame = tk.LabelFrame(frame, text=label)
        self.entries[label] = tk.Entry(label_frame, textvariable=text_var)
        self.entries[label].grid(row=1, column=1, sticky='ew')
        self.entries[label].pack(padx=5, pady=5, expand=1, fill='x')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_button(self, frame, name, row, column):
        self.buttons[name] = tk.Button(frame, width=25, relief=tk.RAISED)
        self.buttons[name]["text"] = name
        self.buttons[name].grid(padx=10, pady=5, row=row, column=column)

    def create_combobox(self, frame, label, values, row, column):
        label_frame = tk.LabelFrame(frame, text=label)
        self.combo_boxes[label] = ttk.Combobox(label_frame, values=values)
        self.combo_boxes[label].grid(row=1, column=1)
        self.combo_boxes[label].pack(padx=5, pady=5, expand=1, fill='x')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_checkbox(self, frame, label, variable, row, column):
        self.check_boxes[label] = ttk.Checkbutton(frame, text=label, variable=variable)
        self.check_boxes[label].grid(padx=10, pady=5, row=row, column=column, sticky='nsew')


class EEG(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self):
        control_frame = tk.Frame(master=self)
