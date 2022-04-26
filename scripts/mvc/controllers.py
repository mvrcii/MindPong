from abc import ABC, abstractmethod
from enum import Enum
from tkinter.messagebox import askyesno, showinfo

from scripts.mvc.view import View, ConfigView, GameView
from scripts.pong.game import End


class Controller(ABC):
    @abstractmethod
    def bind(self, view: View):
        raise NotImplementedError


class GuiState(Enum):
    """
    An Enum Class for the different gui states
    """
    START = 1  # the start button is shown
    STOP = 2  # the stop button is shown
    SAVE = 3  # the start and save button is shown


class ConfigController(Controller):
    def __init__(self, master=None) -> None:
        self.master = master
        self.view = None
        self.data = None
        self.gui_state = GuiState.START
        self.valid_form = True

    def bind(self, view: ConfigView):
        self.view = view
        self.view.create_view()
        self.data = self.master.data_model
        self.init_config_view_values()

        self.reset_gui()
        self.view.buttons["Start Session"].configure(command=self.start_session)
        self.view.buttons["Stop Session"].configure(command=self.stop_session)
        self.view.buttons["Save Session"].configure(command=self.save_session)
        self.view.buttons["Discard Session"].configure(command=self.discard_session)

        self.view.check_buttons["Trial Recording"].configure(command=self.set_trial_recording)

    def init_config_view_values(self):
        self.set_entry_text(self.view.entries["ID"], self.data.subject_id)
        self.set_entry_text(self.view.entries["Age"], self.data.subject_age)
        self.view.combo_boxes["Sex"]['values'] = self.data.valid_subject_sex_values
        self.view.combo_boxes["Sex"].set(self.data.subject_sex)
        self.set_entry_text(self.view.entries["Threshold"], self.data.threshold)
        self.set_entry_text(self.view.entries["f_min"], self.data.f_min)
        self.set_entry_text(self.view.entries["f_max"], self.data.f_max)
        self.view.spin_boxes["window_size"].set(self.data.window_size)
        self.view.spin_boxes["window_offset"].set(self.data.window_offset)
        self.view.spin_boxes["trial_min_duration"].set(self.data.trial_min_duration)
        self.view.check_button_vars["Trial Recording"].set(self.data.trial_recording)

    @staticmethod
    def set_entry_text(entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def start_session(self):
        self.validate_form()
        # Create second top level window
        if self.valid_form:
            self.view.disable_inputs()
            self.master.create_game_window()
            # ToDo: Start the liveplot here
            self.view.hide_button("Start Session")
            self.view.show_button("Stop Session")

    def stop_session(self):
        # Confirmation Popup for stopping the session
        answer = askyesno(title="Confirmation", message="Are you sure that you want to stop the session?")
        if answer:
            self.master.game_window.game_controller.show_end_screen()
            self.view.hide_button("Stop Session")
            from scripts.data.extraction.trial_handler import count_trials

            if count_trials > 0:
                self.view.show_button("Discard Session")
                self.view.show_button("Save Session", column=1)
                showinfo("Information", "%d Trials recorded." % count_trials)
            else:
                self.view.show_button("Start Session")
                showinfo("Information", "There are no trials to save.")

    def save_session(self):
        self.set_comment()
        from scripts.data.extraction.trial_handler import save_session, count_trials
        from scripts.mvc.models import MetaData
        from datetime import datetime

        meta_data = MetaData(sid=self.data.subject_id, age=self.data.subject_age, sex=self.data.subject_sex,
                             comment=self.data.comment, amount_events=2, amount_trials=count_trials)
        file_name = "session-%s-%s" % (self.data.subject_id, datetime.now().strftime("%d%m%Y-%H%M%S"))

        save_session(meta_data.turn_into_np_array(), file_name)
        showinfo("Information", "Successfully saved the session.")
        self.master.destroy_game_window()
        self.reset_gui()

    def discard_session(self):
        self.master.destroy_game_window()
        self.reset_gui()
        pass

    def reset_gui(self):
        self.view.enable_inputs()
        self.view.hide_button("Stop Session")
        self.view.hide_button("Save Session")
        self.view.hide_button("Discard Session")
        self.view.show_button("Start Session", row=0, column=0)

    def validate_form(self):
        """Validates the whole form by calling all the individual validation methods

        If one of the parameters is not valid, the boolean valid_form is set to false.
        :return: None
        """
        self.valid_form = True  # Assume that the form is valid
        self.validate_subject_id()
        self.validate_subject_age()
        self.validate_subject_sex()

        self.validate_threshold()
        self.validate_f_min()
        self.validate_f_max()
        self.validate_frequencies()

        self.validate_window_size()
        self.validate_window_offset()
        self.validate_trial_min_duration()
        self.set_comment()

    def validate_subject_id(self):
        """Validate and set the subject id
        :return: None
        """
        label = "ID"
        try:
            self.data.subject_id = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_subject_age(self):
        """Validate and set the subject age
        :return: None
        """
        label = "Age"
        try:
            self.data.subject_age = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_subject_sex(self):
        """Validate and set the subject sex
        :return: None
        """
        label = "Sex"
        try:
            self.data.subject_sex = self.view.combo_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_threshold(self):
        """Validate and set the threshold
        :return: None
        """
        label = "Threshold"
        try:
            self.data.threshold = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_f_min(self):
        """Validate and set the minimal frequency f_min
        :return: None
        """
        label = "f_min"
        try:
            self.data.f_min = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_f_max(self):
        """Validate and set the maximum frequency f_max
        :return: None
        """
        label = "f_max"
        try:
            self.data.f_max = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_frequencies(self):
        """Validate that f_max is always greater than or equal to f_min and set it in the model.
        :return: None
        """
        f_min_label = "f_min"
        f_max_label = "f_max"
        try:
            f_min = float(self.view.entries[f_min_label].get())
            f_max = float(self.view.entries[f_max_label].get())
            if f_min > f_max:
                self.on_invalid(f_min_label)
                self.on_invalid(f_max_label)
                self.valid_form = False
        except ValueError:
            self.on_invalid(f_min_label)
            self.on_invalid(f_max_label)
            self.valid_form = False

    def validate_window_size(self):
        """Validate and set the window size
        :return: None
        """
        label = "window_size"
        try:
            self.data.window_size = self.view.spin_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_window_offset(self):
        """Validate and set the window offset
        :return: None
        """
        label = "window_offset"
        try:
            self.data.window_offset = self.view.spin_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_trial_min_duration(self):
        """Validate and set the minimum trial duration
        :return: None
        """
        label = "trial_min_duration"
        try:
            self.data.trial_min_duration = self.view.spin_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def set_comment(self):
        """Set the comment content in the model
        :return: None
        """
        self.data.comment = self.view.comment_box.get('1.0', 'end-1c')

    def set_trial_recording(self):
        """Set the trial recording in the model"""
        self.data.trial_recording = self.view.check_button_vars["Trial Recording"].get()

    def on_invalid(self, label):
        self.view.labels[label].config(foreground='red')
        self.valid_form = False

    def on_valid(self, label):
        self.view.labels[label].config(foreground='black')


class GameController(Controller):
    def __init__(self, master=None) -> None:
        self.master = master
        self.view = None
        self.data = None
        self.frames = {}

    def bind(self, view: GameView):
        self.view = view
        self.data = self.master.data_model
        self.view.bind_data(self.data)
        self.view.create_view()

    def show_end_screen(self):
        self.view.game.change(End)

