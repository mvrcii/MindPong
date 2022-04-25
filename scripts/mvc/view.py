import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from abc import abstractmethod

from scripts.pong.game import Game


class View(tk.Frame):
    @abstractmethod
    def create_view(self):
        """Creates the view"""
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
        self.check_buttons = {}
        self.check_button_vars = {}
        self.comment_box = None
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self):
        # Control Frame
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=0, column=0, sticky='nsew')

        # First Column
        self.build_subject_section(control_frame, "Subject", row=0, column=0)
        self.build_algorithm_section(control_frame, "Algorithm", row=1, column=0)
        self.build_trial_section(control_frame, "Trial", row=2, column=0)
        self.build_comment_section(control_frame, "Comment", row=3, column=0)
        self.create_button(control_frame, "Start", row=4, column=0)

        # Second Column
        self.build_graph_section(control_frame, "Graph", row=0, column=1)
        self.build_switch_section(control_frame, row=3, column=1)

    # First Column Sections
    def build_subject_section(self, frame, label, row, column):
        """Frame where the subject information is filled in (id, age, sex).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        label_frame = ttk.LabelFrame(frame, text=label)
        self.create_entry(label_frame, "ID", row=0, column=0, text_var=tk.IntVar(value=1))
        self.create_entry(label_frame, "Age", row=0, column=1, text_var=None)
        self.create_combobox(label_frame, "Sex", values=[], row=0, column=2)
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def build_algorithm_section(self, frame, label, row, column):
        """Frame where the algorithm parameters are filled in (threshold, f_min, f_max, window_size, window_offset).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        label_frame = ttk.LabelFrame(frame, text=label)
        self.create_entry(label_frame, "Threshold", row=0, column=0, text_var=tk.DoubleVar())
        self.create_entry(label_frame, "f_min", row=0, column=1, text_var=tk.DoubleVar())
        self.create_entry(label_frame, "f_max", row=0, column=2, text_var=tk.DoubleVar())
        self.create_spinbox(label_frame, "window_size", "Sliding Window Size", row=1, column=0, from_=200, to=2000,
                            interval=200)
        self.create_spinbox(label_frame, "window_offset", "Sliding Window Offset", row=1, column=1, from_=40, to=400,
                            interval=40)
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def build_trial_section(self, frame, label, row, column):
        """Frame where the trial parameters are filled in (trial_min_duration).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        spinbox_frame = ttk.LabelFrame(frame, text=label)
        self.create_spinbox(spinbox_frame, "trial_min_duration", "Trial Min-Duration", row=0, column=0, from_=800,
                            to=1500, interval=100)
        spinbox_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def build_comment_section(self, frame, label, row, column):
        """Frame where the comment box is placed in.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        comment_box_frame = ttk.LabelFrame(frame, text=label)
        self.comment_box = ScrolledText(comment_box_frame, wrap=tk.WORD, height=4)
        self.comment_box.grid(row=3, column=0, pady=10, padx=10)
        comment_box_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    # Second Column Sections
    def build_graph_section(self, frame, label, row, column):
        """Frame where the checkboxes to toggle the graphs are placed in (C3, C4, C3a, C4a, Label).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        graph_frame = ttk.LabelFrame(frame, text=label)
        self.create_checkbutton(graph_frame, "C3", row=0, column=0, command=None)
        self.create_checkbutton(graph_frame, "C4", row=1, column=0, command=None)
        self.create_checkbutton(graph_frame, "C3a", row=2, column=0, command=None)
        self.create_checkbutton(graph_frame, "C4a", row=3, column=0, command=None)
        self.create_checkbutton(graph_frame, "Label", row=4, column=0, command=None)
        graph_frame.grid(padx=10, pady=5, row=row, column=column, rowspan=2, sticky='nsew')

    def build_switch_section(self, frame, row, column):
        """Frame where the checkboxes to toggle overall settings are placed in (Dark-mode, Trial recording).

        :param any frame: the parent container to place the children in.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        switch_frame = ttk.Frame(frame)
        # Switch to toggle the recording of trials
        self.create_checkbutton(switch_frame, "Trial Recording", row=0, column=0, command=None)
        # Switch for dark/light mode (not persisted in the data model)
        self.create_checkbutton(switch_frame, "Dark-Mode", row=1, column=0, command=self.toggle_dark_mode)
        switch_frame.grid(row=row, column=column, rowspan=2, sticky='sew')

    # Helper functions
    def create_entry(self, frame, label, row, column, text_var):
        """Creates an entry field with the given parameters.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :param any text_var: the text variable.
        :return: None
        """
        self.labels[label] = ttk.Label(text=label)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.entries[label] = ttk.Entry(label_frame, textvariable=text_var)
        self.entries[label].grid(padx=5, pady=5, row=1, column=1, sticky='nsew')
        self.entries[label].pack(padx=5, pady=5, expand=1, fill='x')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_button(self, frame, label, row, column):
        """Creates a button with the given parameters.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for the button.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        self.buttons[label] = ttk.Button(frame, text=label)
        self.buttons[label].grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_combobox(self, frame, label, values, row, column):
        """Creates a combobox with the given parameters

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for the label frame.
        :param any values: the list of possible values to be selected.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        self.labels[label] = ttk.Label(text=label)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.combo_boxes[label] = ttk.Combobox(label_frame, state="readonly", values=values)
        self.combo_boxes[label].grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_checkbutton(self, frame, label, row, column, command):
        """Creates a checkbutton with the given parameters.

        By default, the on value is True and the off value is False.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for the checkbutton.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :param any command: the command that is triggered when the checkbutton state changes.
        :return: None
        """
        self.check_button_vars[label] = tk.BooleanVar()
        self.check_buttons[label] = ttk.Checkbutton(frame, text=label, style='Switch.TCheckbutton',
                                                    variable=self.check_button_vars[label],
                                                    onvalue=True, offvalue=False, command=command)
        self.check_buttons[label].grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def create_spinbox(self, frame, label, text, row, column, from_, to, interval):
        """Creates a spinbox with the given parameters.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for referencing the label and the spinbox itself.
        :param str text: the text which is used for the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :param int from_: the value for the interval start.
        :param int to: the value for the interval end.
        :param int interval: the value for the spacing of individual values in the interval.
        :return: None
        """
        self.labels[label] = ttk.Label(text=text)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.spin_boxes[label] = ttk.Spinbox(label_frame, state="readonly", from_=from_, to=to, increment=interval)
        self.spin_boxes[label].grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def toggle_dark_mode(self):
        """Toggles the config view between dark and light mode."""
        if self.check_button_vars["Dark-Mode"].get():
            self.master.call("set_theme", "dark")
        else:
            self.master.call("set_theme", "light")


class GameView(View):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky='nsew')
        self.data = None
        self.frames = {}
        self.mind_pong = None

    def bind_data(self, data):
        self.data = data

    def create_view(self):
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=1, column=1, sticky='nsew')

        frame = Game(control_frame, self, self.data)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.focus_set()
        frame.tkraise()
