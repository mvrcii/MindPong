import time
from abc import ABC, abstractmethod
from tkinter.messagebox import askyesno, showinfo

from scripts.config import CALIBRATION_TIME
from scripts.data.extraction import trial_handler
from scripts.mvc.view import View, ConfigView, GameView
from scripts.pong.game import End
from scripts.data.extraction.trial_handler import save_session
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
        self.calibration_timer = 0

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
        self.view.buttons["Abort"].configure(command=self.__abort_calibration)
        self.view.check_buttons["Trial Recording"].configure(command=self.__set_trial_recording)
        self.view.check_buttons["Plot"].configure(command=self.__toggle_plot)

    def __init_config_view_values(self):
        """Initially configures the view with the model data"""
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

    def update(self):
        self.__update_calibration()

        # Update the plot if plot is shown and the session is recording
        if self.view.check_button_vars["Plot"].get() and self.data.session_recording:
            perform_live_plot()

    @staticmethod
    def __set_entry_text(entry, value):
        """Helper method to set the text of an entry field"""
        entry.delete(0, "end")
        entry.insert(0, value)

    def __start_calibration(self):
        """Starts the calibration"""
        self.view.show_button("Abort", row=0, column=0)
        self.view.show_progress_bar(row=0, column=1)
        self.calibration_timer = time.time()

    def __update_calibration(self):
        """Updates the calibration timer and starts the game afterwards"""
        if self.calibration_timer > 0:
            percentage = round((time.time() - self.calibration_timer) / CALIBRATION_TIME * 100, 2)
            self.view.set_progress_bar_value(percentage)

            if percentage >= 100:
                if self.data.trial_recording:
                    # Saves a trial that includes the calibration when the trial recording is switched on
                    trial_handler.mark_trial(self.calibration_timer, time.time(), trial_handler.Labels.CALIBRATION)
                self.__stop_calibration()
                self.view.hide_button("Abort")
                self.view.show_button("Stop Session")
                self.master.game_window.game_controller.start_game()

    def __stop_calibration(self):
        """Stops the calibration"""
        self.view.hide_progress_bar()
        self.calibration_timer = 0

    def __abort_calibration(self):
        """Aborts the calibration and resets everything."""
        answer = askyesno(title="Abort", message="Are you sure that you want to abort the calibration?")
        if answer:
            self.__stop_calibration()
            self.__discard_session()

    def __start_session(self):
        """Starts the session, if the input fields are valid, by disabling the input fields, starting the game
        window and the liveplot."""
        self.validate_form()

        # Create second top level window if the form was valid
        if self.valid_form:
            self.view.disable_inputs()
            self.view.hide_button("Start Session")
            self.__start_calibration()
            self.__start_liveplot()
            self.master.create_game_window()

    def __stop_session(self):
        """Stops the current session and changes the view according to the amount of recorded trials."""
        answer = askyesno(title="Confirmation", message="Are you sure that you want to stop the session?")
        if answer:
            self.master.game_window.game_controller.show_end_screen()
            self.view.hide_button("Stop Session")

            # Only allow saving if trial recording is turned on
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
        """Discards the current session."""
        self.view.reset_view()
        self.master.destroy_game_window()

    def __start_liveplot(self):
        """Binds the plot figure to the liveplot script and shows the plot if the toggle is activated"""
        start_live_plot(self.view.figure)

        if self.view.check_button_vars["Plot"].get():
            self.view.show_plot(True)

    def __toggle_plot(self):
        """Toggles the visibility of the plot"""
        if self.view.check_button_vars["Plot"].get() and self.data.session_recording:
            self.view.show_plot(True)
        else:
            self.view.show_plot(False)

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
        # ToDo: Im dark-mode branch ergänzen, sobald der boolean im Datenmodell vorhanden ist
        # text_color = 'white'
        # if self.data.dark_mode:
        #   text_color = 'black'
        # self.view.labels[label].config(foreground=text_color)
        self.view.labels[label].config(foreground='black')
        pass


class GameController(Controller):
    def __init__(self, master=None) -> None:
        self.master = master
        self.view = None

    def bind(self, view: GameView):
        self.view = view
        self.view.bind_data(self.master.data_model)
        self.view.create_view()

    def start_game(self):
        """Starts the game view in the second window"""
        self.master.title("Game")
        self.view.start_game()

    def show_end_screen(self):
        """Stops the game and shows the end screen"""
        self.view.game.change(End)

