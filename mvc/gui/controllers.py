from abc import ABC, abstractmethod
from mvc.gui.view import View, ConfigView, EEGView
from mvc.gui.models import ConfigData


class Controller(ABC):
    @abstractmethod
    def bind(self, view: View):
        raise NotImplementedError


class ConfigController(Controller):
    def __init__(self, master=None) -> None:
        self.master = master
        self.view = None
        self.config_data = ConfigData()  # initialize the data model
        self.valid_form = True

    def bind(self, view: ConfigView):
        self.view = view
        self.view.create_view()
        self.init_config_view_values()
        self.view.buttons["Start"].configure(command=self.start)

    def init_config_view_values(self):
        self.set_entry_text(self.view.entries["ID"], self.config_data.subject_id)
        self.set_entry_text(self.view.entries["Age"], self.config_data.subject_age)
        self.view.combo_boxes["Sex"]['values'] = self.config_data.valid_subject_sex_values
        self.view.combo_boxes["Sex"].set(self.config_data.subject_sex)
        self.set_entry_text(self.view.entries["Threshold"], self.config_data.threshold)
        self.set_entry_text(self.view.entries["f_min"], self.config_data.f_min)
        self.set_entry_text(self.view.entries["f_max"], self.config_data.f_max)
        self.view.spin_boxes["window_size"].set(self.config_data.window_size)
        self.view.spin_boxes["window_offset"].set(self.config_data.window_offset)
        self.view.spin_boxes["trial_min_duration"].set(self.config_data.trial_min_duration)

    @staticmethod
    def set_entry_text(entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def start(self):
        self.validate_form()

        # Create second top level window
        if self.valid_form:
            self.master.create_second_window()
            print(self.config_data.__dict__)

    def validate_form(self):
        """
        Validates the whole form by calling all the individual validation methods

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

    def validate_subject_id(self):
        """
        Validate the subject id
        :return:
        """
        label = "ID"
        try:
            self.config_data.subject_id = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_subject_age(self):
        """
        Validate the subject age
        :return: None
        """
        label = "Age"
        try:
            self.config_data.subject_age = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_subject_sex(self):
        """
        Validate the subject sex
        :return: None
        """
        label = "Sex"
        try:
            self.config_data.subject_sex = self.view.combo_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_threshold(self):
        """
        Validate the threshold
        :return: None
        """
        label = "Threshold"
        try:
            self.config_data.threshold = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_f_min(self):
        """
        Validate the minimal frequency f_min
        :return: None
        """
        label = "f_min"
        try:
            self.config_data.f_min = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_f_max(self):
        """
        Validate the maximum frequency f_max
        :return: None
        """
        label = "f_max"
        try:
            self.config_data.f_max = self.view.entries[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_frequencies(self):
        """
        Validate that f_max is always greater than or equal to f_min
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
        """
        Validate the window size
        :return: None
        """
        label = "window_size"
        try:
            self.config_data.window_size = self.view.spin_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_window_offset(self):
        """
        Validate the window offset
        :return: None
        """
        label = "window_offset"
        try:
            self.config_data.window_offset = self.view.spin_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def validate_trial_min_duration(self):
        """
        Validate the minimum trial duration
        :return: None
        """
        label = "trial_min_duration"
        try:
            self.config_data.trial_min_duration = self.view.spin_boxes[label].get()
        except ValueError:
            self.on_invalid(label)
        else:
            self.on_valid(label)

    def on_invalid(self, label):
        self.view.labels[label].config(foreground='red')
        self.valid_form = False

    def on_valid(self, label):
        self.view.labels[label].config(foreground='black')


class EEGController(Controller):
    def __init__(self) -> None:
        self.view = None

    def bind(self, view: EEGView):
        self.view = view
        self.view.create_view()

