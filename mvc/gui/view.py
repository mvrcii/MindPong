import tkinter as tk
import tkinter.ttk as ttk
from abc import abstractmethod


class View(tk.Frame):
    @abstractmethod
    def create_view(self):
        raise NotImplementedError


class ConfigView(View):
    def __init__(self, master):
        super().__init__(master)
        self.spin_boxes = {}
        self.sliders = {}
        self.entries = {}
        self.labels = {}
        self.buttons = {}
        self.combo_boxes = {}
        self.switches = {}
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self):
        # Control Frame
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=0, column=0, sticky='nsew')

        self.build_subject_section(control_frame, "Subject", row=0, column=0)
        self.build_graph_section(control_frame, "Graph", row=0, column=1)
        self.build_algorithm_section(control_frame, "Algorithm", row=1, column=0)
        self.build_window_section(control_frame, "Window", row=2, column=0)
        self.create_button(control_frame, "Start", row=3, column=0)

        # Switch for dark/light mode
        self.create_switch(control_frame, "Dark-Mode", row=3, column=1, variable=tk.BooleanVar(),
                           command=self.toggle_dark_mode)

    def build_graph_section(self, frame, label, row, column):
        graph_frame = ttk.LabelFrame(frame, text=label)
        self.create_switch(graph_frame, "C3", row=0, column=0, variable=tk.BooleanVar(), command=None)
        self.create_switch(graph_frame, "C4", row=1, column=0, variable=tk.BooleanVar(), command=None)
        graph_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def build_subject_section(self, frame, label, row, column):
        label_frame = ttk.LabelFrame(frame, text=label)
        self.create_entry(label_frame, "ID", row=0, column=0, text_var=tk.IntVar(value=1))
        self.create_entry(label_frame, "Age", row=0, column=1, text_var=None)
        self.create_combobox(label_frame, "Sex", values=[], row=0, column=2)
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def build_algorithm_section(self, frame, label, row, column):
        label_frame = ttk.LabelFrame(frame, text=label)
        self.create_entry(label_frame, "Threshold", row=0, column=0, text_var=tk.DoubleVar())
        self.create_entry(label_frame, "f_min", row=0, column=1, text_var=tk.DoubleVar())
        self.create_entry(label_frame, "f_max", row=0, column=2, text_var=tk.DoubleVar())
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def build_window_section(self, frame, label, row, column):
        spinbox_frame = ttk.LabelFrame(frame, text=label)
        self.create_spinbox(spinbox_frame, "window_size", "Window Size", row=0, column=0, from_=200, to=2000, interval=200)
        self.create_spinbox(spinbox_frame, "window_offset", "Window Offset", row=0, column=1, from_=40, to=400, interval=40)
        self.create_spinbox(spinbox_frame, "trial_min_duration", "Trial Min-Duration", row=0, column=2, from_=800, to=1500, interval=100)
        spinbox_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    # Helper functions
    def create_entry(self, frame, label, row, column, text_var):
        self.labels[label] = ttk.Label(text=label)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.entries[label] = ttk.Entry(label_frame, textvariable=text_var)
        self.entries[label].grid(padx=5, pady=5, row=1, column=1, sticky='nsew')
        self.entries[label].pack(padx=5, pady=5, expand=1, fill='x')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_button(self, frame, name, row, column):
        self.buttons[name] = ttk.Button(frame, text=name)
        self.buttons[name].grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_combobox(self, frame, label, values, row, column):
        self.labels[label] = ttk.Label(text=label)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.combo_boxes[label] = ttk.Combobox(label_frame, state="readonly", values=values)
        self.combo_boxes[label].grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_switch(self, frame, label, variable, row, column, command):
        self.switches[label] = variable
        check_button = ttk.Checkbutton(frame, text=label, style='Switch.TCheckbutton', variable=variable,
                                       onvalue=True, offvalue=False, command=command)
        check_button.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_spinbox(self, frame, label, text, row, column, from_, to, interval):
        self.labels[label] = ttk.Label(text=text)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.spin_boxes[label] = ttk.Spinbox(label_frame, state="readonly", from_=from_, to=to, increment=interval)
        self.spin_boxes[label].grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def toggle_dark_mode(self):
        if self.switches["Dark-Mode"].get():
            self.master.call("set_theme", "dark")
        else:
            self.master.call("set_theme", "light")


class GameView(View):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self):
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.grid(row=0, column=0, sticky='nsew')

        tk.Label(control_frame, text="FRAME 1").grid(row=0, column=0, sticky='nsew')
        tk.Label(control_frame, text="FRAME 2").grid(row=0, column=1, sticky='nsew')

