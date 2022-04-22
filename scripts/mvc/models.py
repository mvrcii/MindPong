class ConfigData(object):
    def __init__(self,
                 subject_id: int = 1,
                 subject_age: int = 1,
                 subject_sex: str = 'D',
                 threshold: float = 0.5,
                 f_min: float = 5,
                 f_max: float = 10,
                 window_size: int = 1000,
                 window_offset: int = 200,
                 trial_min_duration: int = 1000,
                 comment: str = '',
                 trial_recording: bool = True):
        
        self.__subject_id = subject_id
        self.__subject_age = subject_age
        self.__subject_sex = subject_sex
        self.__threshold = threshold
        self.__f_min = f_min
        self.__f_max = f_max
        self.__window_size = window_size
        self.__window_offset = window_offset
        self.__trial_min_duration = trial_min_duration
        self.__comment = comment
        self.__trial_recording = trial_recording
        self.__valid_subject_sex_values = ['M', 'F', 'D']

    @property
    def subject_id(self):
        return self.__subject_id

    @property
    def subject_age(self):
        return self.__subject_age

    @property
    def subject_sex(self):
        return self.__subject_sex
    
    @property
    def threshold(self):
        return self.__threshold
    
    @property
    def f_min(self):
        return self.__f_min
    
    @property
    def f_max(self):
        return self.__f_max
    
    @property
    def window_size(self):
        return self.__window_size
    
    @property
    def window_offset(self):
        return self.__window_offset
    
    @property
    def trial_min_duration(self):
        return self.__trial_min_duration

    @property
    def comment(self):
        return self.__comment

    @property
    def trial_recording(self):
        return self.__trial_recording

    @property
    def valid_subject_sex_values(self):
        return self.__valid_subject_sex_values

    @subject_id.setter
    def subject_id(self, value):
        """
        Validate the subject id
        :param int value: the new value for the subject id
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        if int(value) > 0:
            self.__subject_id = value
        else:
            raise ValueError(f'Invalid subject id: {value}')

    @subject_age.setter
    def subject_age(self, value):
        """
        Validate the age
        :param int value: the new value for the age
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        if 0 < int(value) <= 100:
            self.__subject_age = value
        else:
            raise ValueError(f'Invalid age: {value}')

    @subject_sex.setter
    def subject_sex(self, value: str):
        """
        Validate the sex
        :param str value: the new value for the sex
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        if value in self.__valid_subject_sex_values:
            self.__subject_sex = value
        else:
            raise ValueError(f'Invalid sex: {value}')

    @threshold.setter
    def threshold(self, value: float):
        """
        Validate the threshold
        :param float value: the new value for the threshold
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        value = float(value)
        if 0.0 <= value <= 1.0:
            self.__threshold = value
        else:
            raise ValueError(f'Invalid threshold: {value}')

    @f_min.setter
    def f_min(self, value: float):
        """
        Validate the f_min
        :param float value: the new value for the f_min
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        value = float(value)
        if 0.0 <= value:
            self.__f_min = value
        else:
            raise ValueError(f'Invalid f_min: {value}')
        
    @f_max.setter
    def f_max(self, value: float):
        """
        Validate the f_max
        :param float value: the new value for the f_max
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        value = float(value)
        if 0.0 <= value:
            self.__f_max = value
        else:
            raise ValueError(f'Invalid f_max: {value}')
        
    @window_size.setter
    def window_size(self, value: int):
        """
        Validate the window_size
        :param float value: the new value for the window_size
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        value = int(value)
        if 200 <= value <= 2000 and value % 200 == 0:
            self.__window_size = value
        else:
            raise ValueError(f'Invalid window_size: {value}')

    @window_offset.setter
    def window_offset(self, value: int):
        """
        Validate the window_offset
        :param float value: the new value for the window offset
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        value = int(value)
        if 40 <= value <= 400 and value % 40 == 0:
            self.__window_offset = value
        else:
            raise ValueError(f'Invalid window_offset: {value}')
        
    @trial_min_duration.setter
    def trial_min_duration(self, value: int):
        """
        Validate the minimal trial duration
        :param float value: the new value for the minimal trial min duration
        :raise ValueError: if the given value is incorrect
        :return: None
        """
        value = int(value)
        if 800 <= value <= 1500 and value % 100 == 0:
            self.__trial_min_duration = value
        else:
            raise ValueError(f'Invalid trial_min_duration: {value}')

    @comment.setter
    def comment(self, value: str):
        """
        Setter for the comment variable
        :param str value: the new value for the comment
        :return: None
        """
        self.__comment = value

    @trial_recording.setter
    def trial_recording(self, value: bool):
        """
        Setter for the trial recording variable

        By default, the trial recording is set to true.
        If set to true, the trials will be recorded during the session.

        :param bool value: the new value for the trial recording
        :return: None
        """
        self.__trial_recording = value

    # Currently without persistence of the Config data
    # Variables in the Model will always be overridden when the start button is pressed
    def load(self):
        """
        Load the config from a file
        :return: ConfigData
        """
        # TODO: Deserialize the file and load the config
        # with open('emails.txt', 'r') as f:
        #     lines = f.readlines()
        pass

    def save(self):
        """
        Save the email into a file
        :return:
        """
        # TODO: Serialize the config and save it to a file
        # with open('emails.txt', 'a') as f:
        #     f.write(self.sid + '\n')
        pass
