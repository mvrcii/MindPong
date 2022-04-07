import datetime
import numpy as np


class MetaData:
    """
    Class to store the meta data of one trial in an object
    """
    __subject_ID: int
    __date: datetime.date
    __time: datetime.time
    __amount_samples: int
    __sampling_rate: int
    __channel_mapping: np.ndarray
    __amount_trials: int

    # channel configuration of the headset we use
    bci_channels = ['C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1',
                    'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2', 'CP6']

    def __init__(self, sid, amount_samples, amount_trials, time=datetime.datetime.now().time(), sampling_rate=125,
                 channels=bci_channels):
        """
        Date of the session is automatically the current date
        :param sid: ID of the subject
        :param amount_samples: amount of the EEG data samples in this trial
        :param time: start time of the trial
        :param sampling_rate: sampling rate
        :param channels: used channel occupancy as string array
        :param amount_trials: amount of trails in this session
        """
        self.__subject_ID = sid
        self.__date = datetime.date.today()
        self.__time = time
        self.__amount_samples = amount_samples
        self.__sampling_rate = sampling_rate
        self.__channel_mapping = channels
        self.__amount_trials = amount_trials

    @property
    def subject_ID(self):
        return self.__subject_ID

    @property
    def date(self):
        return self.__date

    def date_to_string(self) -> str:
        return self.date.strftime("%m/%d/%Y")

    @property
    def time(self):
        return self.__time


    @property
    def amount_samples(self):
        return self.__amount_samples

    @property
    def sampling_rate(self):
        return self.__sampling_rate

    @property
    def channel_mapping(self):
        return self.__channel_mapping


    @property
    def amount_trials(self):
        return self.__amount_trials

    def turn_into_np_array(self) -> np.ndarray:
        """
        Creates a numpy array filled with tuples
        Every tuples get the attribute name and the respective attribute
        :return: np.ndarray with meta data
        """
        meta = [('id', self.subject_ID), ('date', self.date), ('time', self.time),
                ('amount_samples', self.amount_samples),
                ('sampling_rate', self.sampling_rate), ('channels', self.channel_mapping),
                ('amount_trials', self.amount_trials)]
        return np.array(meta, dtype=object)


