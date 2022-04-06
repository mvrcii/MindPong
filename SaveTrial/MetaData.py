import datetime


class MetaData:
    __subject_ID = 1
    __date: datetime.date
    __time: datetime.time
    __amount_samples: int
    __sampling_rate: int


    def __init__(self, sid=1, time=datetime.datetime.now().time(), amount_samples=0, sampling_rate=125):
        self.__subject_ID = sid
        self.__date = datetime.date.today()
        self.__time = time
        self.__amount_samples = amount_samples
        self.__sampling_rate = sampling_rate

    def get_subject_ID(self):
        return self.__subject_ID

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    def get_amount_samples(self):
        return self.__amount_samples

    def get_sampling_rate(self):
        return self.__sampling_rate



