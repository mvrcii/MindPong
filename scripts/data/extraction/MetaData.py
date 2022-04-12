import datetime
import numpy as np


class MetaData:
    """
    Class to store the meta-data of one trial in an object
    """
    __subject_ID: int
    __subject_sex: str
    __subject_age: int
    __date: datetime.date
    __time: datetime.time
    __sampling_rate: int = 125
    __channel_mapping: np.ndarray
    __recording_type: str
    __headset: str
    __amount_trials: int
    __comment: str
    __amount_different_events: int

    # channel configuration of the headset we use
    bci_channels = ['C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1', 'O2', 'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2', 'CP6']

    def __init__(self, sid, sex, age, amount_trials, comment, amount_events, time=datetime.datetime.now().time(),
                 sampling_rate=125, channel_mapping=bci_channels, recording_type='game', headset='BCI'):
        """
        Date of the session is automatically the current date
        :param sid: ID of the subject
        :param sex: sex of the subject
        :param age: age of the subject
        :param comment: comment section for the scientist
        :param amount_events: amount of different events in one session
        :param time: start time of the trial
        :param sampling_rate: sampling rate
        :param channel_mapping: used channel occupancy as string numpy array
        :param recording_type: the way the data was collected (e.g. game, arrows, ...)
        :param headset: kind of headset which is used for data acquisition
        :param amount_trials: amount of trails in this session
        """
        self.__subject_ID = sid
        self.__subject_sex = sex
        self.__subject_age = age
        self.__date = datetime.date.today()
        self.__time = time
        self.__sampling_rate = sampling_rate
        self.__channel_mapping = channel_mapping
        self.__amount_trials = amount_trials
        self.__recording_type = recording_type
        self.__headset = headset
        self.__amount_different_events = amount_events
        self.__comment = comment

    def turn_into_np_array(self) -> np.ndarray:
        """
        Creates a numpy array filled with tuples
        Every tuples get the attribute name and the respective attribute
        :return: np.ndarray with meta-data
        """
        meta = [['id', self.__subject_ID], ['sex', self.__subject_sex], ['age', self.__subject_age],
                ['date', self.__date], ['time', self.__time],
                ['sampling_rate', self.__sampling_rate], ['channels', self.__channel_mapping],
                ['recording_type', self.__recording_type], ['headset', self.__headset],
                ['amount_trials', self.__amount_trials], ['different_events', self.__amount_different_events],
                ['comment', self.__comment]]
        return np.array(meta, dtype=object)
