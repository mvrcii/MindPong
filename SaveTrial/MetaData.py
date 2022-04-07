import datetime



class MetaData:

    """
    Class to store the meta data of one trial in an object
    """
    __subject_ID: int
    __date: datetime.date
    __time: datetime.time
    __amount_samples: int
    __sampling_rate: int

    def __init__(self, sid, amount_samples, time=datetime.datetime.now().time(), sampling_rate=125):
        """
        Date of the session is automatically the current date
        :param sid: ID of the subject
        :type sid: int
        :param amount_samples: amount of the EEG data samples in this trial
        :type amount_samples: int
        :param time: start time of the trial
        :type time: datetime.time
        :param sampling_rate: sampling rate
        :type sampling_rate: int
        """
        self.__subject_ID = sid
        self.__date = datetime.date.today()
        self.__time = time
        self.__amount_samples = amount_samples
        self.__sampling_rate = sampling_rate

    @property
    def subject_ID(self):
        return self.__subject_ID

    @property
    def date(self):
        return self.__date

    @property
    def time(self):
        return self.__time

    @property
    def amount_samples(self):
        return self.__amount_samples

    @property
    def sampling_rate(self):
        return self.__sampling_rate


