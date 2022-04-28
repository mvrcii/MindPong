from abc import ABC, abstractmethod
from tkinter.messagebox import askyesno, showinfo

from scripts.mvc.view import View, ConfigView, GameView
from scripts.pong.game import End
from scripts.data.extraction.trial_handler import save_session, count_trials, count_event_types
from scripts.mvc.models import MetaData
from datetime import datetime
from scripts.data.visualisation.liveplot_matlab import start_live_plot, perform_live_plot


class Controller(ABC):
    @abstractmethod
    def bind(self, view: View):
        raise NotImplementedError


class ConfigController(Controller):
    def __init__(self, master=None) -> None:
        self.master = master
        self.view = None
        self.data = None
        self.valid_form = True

    def bind(self, view: ConfigView):
        self.view = view
        self.view.create_view()
        self.data = self.master.data_model

        self.__init_config_view_values()
        self.view.reset_view()

        self.view.buttons["Start Session"].configure(command=self.__start_session)
        self.view.buttons["Stop Session"].configure(command=self.__stop_session)
        self.view.buttons["Save Session"].configure(command=self.__save_session)
        self.view.buttons["Discard Session"].configure(command=self.__discard_session)
        self.view.check_buttons["Trial Recording"].configure(command=self.__set_trial_recording)

    def update(self):
        # Update the plot if plot is shown
        if self.view.check_button_vars["Plot"].get():
            perform_live_plot()

    def __init_config_view_values(self):
        self.__set_entry_text(self.view.entries["ID"], self.data.subject_id)
        self.__set_entry_text(self.view.entries["Age"], self.data.subject_age)
        self.view.combo_boxes["Sex"]['values'] = self.data.valid_subject_sex_values
        self.view.combo_boxes["Sex"].set(self.data.subject_sex)
        self.__set_entry_text(self.view.entries["Threshold"], self.data.threshold)
        self.__set_entry_text(self.view.entries["f_min"], self.data.f_min)
        self.__set_entry_text(self.view.entries["f_max"], self.data.f_max)
        self.view.spin_boxes["window_size"].set(self.data.window_size)
        self.view.spin_boxes["window_offset"].set(self.data.window_offset)
        self.view.spin_boxes["trial_min_duration"].set(self.data.trial_min_duration)
        self.view.check_button_vars["Trial Recording"].set(self.data.trial_recording)

    @staticmethod
    def __set_entry_text(entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def __start_session(self):
        """Starts the session, if the input fields are valid, by disabling the input fields, starting the game
        window and the liveplot.

        :return: None
        """
        self.validate_form()
        # Create second top level window
        if self.valid_form:
            self.view.disable_inputs()

            self.master.create_game_window()
            self.__start_liveplot()

            self.view.hide_button("Start Session")
            self.view.show_button("Stop Session")

    def __start_liveplot(self):
        start_live_plot(self.view.figure)

    def __stop_session(self):
        """Stops the current session and changes the view according to the amount of recorded trials.

        :return: None
        """
        answer = askyesno(title="Confirmation", message="Are you sure that you want to stop the session?")
        if answer:
            self.master.game_window.game_controller.show_end_screen()
            self.view.hide_button("Stop Session")

            if self.data.trial_recording:
                from scripts.data.extraction.trial_handler import count_trials
                if count_trials > 0:
                    self.view.show_button("Discard Session")
                    self.view.show_button("Save Session", column=1)
                    showinfo("Information", "%d Trial(s) recorded." % count_trials)
                else:
                    showinfo("Information", "There are no trials to save.")
                    self.__discard_session()
            else:
                self.__discard_session()

    def __save_session(self):
        """Creates a MetaData object and saves the current session.

        Also closes the game window and resets the ConfigView.
        :return: None
        """
        self.__set_comment()
        from scripts.data.extraction.trial_handler import count_trials, count_event_types
        meta_data = MetaData(sid=self.data.subject_id, age=self.data.subject_age, sex=self.data.subject_sex,
                             comment=self.data.comment, amount_events=count_event_types, amount_trials=count_trials)
        print(meta_data.__str__())
        file_name = "session-%s-%s" % (self.data.subject_id, datetime.now().strftime("%d%m%Y-%H%M%S"))

        save_session(meta_data.turn_into_np_array(), file_name)
        showinfo("Information", "Successfully saved the session.")
        self.master.destroy_game_window()
        self.view.reset_view()

    def __discard_session(self):
        """Discards the current session.

        :return: None
        """
        self.master.destroy_game_window()
        self.view.reset_view()
        pass

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
        self.__set_comment()

    def validate_subject_id(self):
        """Validate and set the subject id
        :return: None
        """
        label = "ID"
        try:
            self.data.subject_id = self.view.entries[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_subject_age(self):
        """Validate and set the subject age
        :return: None
        """
        label = "Age"
        try:
            self.data.subject_age = self.view.entries[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_subject_sex(self):
        """Validate and set the subject sex
        :return: None
        """
        label = "Sex"
        try:
            self.data.subject_sex = self.view.combo_boxes[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_threshold(self):
        """Validate and set the threshold
        :return: None
        """
        label = "Threshold"
        try:
            self.data.threshold = self.view.entries[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_f_min(self):
        """Validate and set the minimal frequency f_min
        :return: None
        """
        label = "f_min"
        try:
            self.data.f_min = self.view.entries[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_f_max(self):
        """Validate and set the maximum frequency f_max
        :return: None
        """
        label = "f_max"
        try:
            self.data.f_max = self.view.entries[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

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
                self.__on_invalid(f_min_label)
                self.__on_invalid(f_max_label)
                self.valid_form = False
        except ValueError:
            self.__on_invalid(f_min_label)
            self.__on_invalid(f_max_label)
            self.valid_form = False

    def validate_window_size(self):
        """Validate and set the window size
        :return: None
        """
        label = "window_size"
        try:
            self.data.window_size = self.view.spin_boxes[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_window_offset(self):
        """Validate and set the window offset
        :return: None
        """
        label = "window_offset"
        try:
            self.data.window_offset = self.view.spin_boxes[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def validate_trial_min_duration(self):
        """Validate and set the minimum trial duration
        :return: None
        """
        label = "trial_min_duration"
        try:
            self.data.trial_min_duration = self.view.spin_boxes[label].get()
        except ValueError:
            self.__on_invalid(label)
        else:
            self.__on_valid(label)

    def __set_comment(self):
        """Set the comment content in the model
        :return: None
        """
        self.data.comment = self.view.comment_box.get('1.0', 'end-1c')

    def __set_trial_recording(self):
        """Set the trial recording in the model"""
        self.data.trial_recording = self.view.check_button_vars["Trial Recording"].get()

    def __on_invalid(self, label):
        self.view.labels[label].config(foreground='red')
        self.valid_form = False

    def __on_valid(self, label):
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

