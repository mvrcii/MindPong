import time

import numpy as np

from SaveTrial.Labels import Labels

raw_data = [[] for _ in range(16)]
event_type = []
event_pos = []
event_duration = []
start_time: time.time()


def send_raw_data(data, start: time.time()=None):
    """
    Start time of the session is passed only at the first data transfer of the session
    (1) If start is not None the time stamp of the start of session get saved in start_time
    (2) Sended data get saved in raw_data
    :param data: raw data from the data acquisition
    :param start: time stamp of the start of the session
    """
    if(start is not None):
        global start_time
        start_time = start
    for i in range(len(raw_data)):
        raw_data[i].append(data[i][0])


def mark_trial(start: time.time(), end: time.time(), label: Labels.Labels):
    """
    (1) Calculation of the trial position in raw_data
    (2) Calculation of the duration of the trial
    (3) Saves the duration of the trial in event_duration
    (4) Saves the label of the trial in event_type
    (5) Saves the trial position in event_pos
    :param start: time stamp of the start of the trial
    :param end: time stamp of the end of the trial
    :param label: event_type of the trial
    """
    pos = int((start_time - start) / 0.008)
    duration = int((end - start)/0.008)
    event_duration.append(duration)
    event_type.append(label)
    event_pos.append(pos)



def create_raw_data_array() -> np.ndarray:
    """
    Converts the buffer with the trials to a np.ndarray and clears the buffer
    :return: raw data in a np.ndarray
    """
    global raw_data
    data = np.array(raw_data)
    raw_data = [[] for _ in range(16)]
    return data

def create_event_type_array()-> np.ndarray:
    """
    Converts the buffer with the event types to a np.ndarray and clears the buffer
    :return: event types in a np.ndarray
    """
    global event_type
    et = np.array(event_type)
    event_type.clear()
    return et

def create_position_array() -> np.ndarray:
    """
    Converts the buffer with the positions of the events to a np.ndarray and clears the buffer
    :return: positions of the events in a np.ndarray
    """
    global event_pos
    pos = np.array(event_pos)
    event_pos.clear()
    return pos

def create_duration_array() -> np.ndarray:
    """
    Converts the buffer with the durations of the events to a np.ndarray and clears the buffer
    :return: durations of the events in a np.ndarray
    """
    global event_duration
    duration = np.array(event_duration)
    event_duration.clear()
    return duration

def save_session(metadata: np.ndarray, npz_name: str):
    """
    Save the metadata, the raw data, the event types and the position of the events of one session in a npz-file
    :param metadata: metadata of the session in a np.ndarray
    :param npz_name: name of the npz-file, not the path name!
    """
    name = '../Session/' + npz_name
    print(name)
    np.savez(name, meta=metadata, raw_data=create_raw_data_array(), event_type=create_event_type_array(),
             event_pos=create_position_array(), event_duration=create_duration_array())
