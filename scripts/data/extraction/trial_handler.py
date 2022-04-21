import os.path
import time
import brainflow
import numpy as np
from brainflow import BoardShim
from scripts.pong.player import Labels

number_channels = len(BoardShim.get_eeg_channels(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD))

# time which is needed for one sample in s, T = 1/f = 1/125 = 0.008
time_for_one_sample = 1 / BoardShim.get_sampling_rate(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)

raw_data = [[] for _ in range(number_channels)]
event_type = []
event_pos = []
event_duration = []
start_time: time.time()


def send_raw_data(data, start: time.time() = None):
    """
    Start time of the session is passed only at the first data transfer of the session
    (1) If start is not None the time stamp of the start of session get saved in start_time
    (2) Sent data get saved in raw_data
    :param data[] data: raw data from the data acquisition
    :param time.time() start: time stamp of the start of the session
    :return: None
    """

    if start is not None:
        global start_time
        start_time = start
    for i in range(len(raw_data)):
        raw_data[i].append(data[i][0])


def mark_trial(start: time.time(), end: time.time(), label: Labels):
    """
    (1) Calculation of the trial position in raw_data
    (2) Calculation of the duration of the trial
    (3) Saves the duration of the trial in event_duration
    (4) Saves the label of the trial in event_type
    (5) Saves the trial position in event_pos
    :param time.time() start: time stamp of the start of the trial
    :param time.time() end: time stamp of the end of the trial
    :param Labels label: event_type of the trial
    :return: None
    """

    global start_time
    pos = round((start - start_time) / time_for_one_sample)
    duration = round((end - start) / time_for_one_sample)
    event_duration.append(duration)
    event_type.append(label)
    event_pos.append(pos)
    print("Finished storing")


def create_raw_data_array() -> np.ndarray:
    """
    Converts the buffer with the trials to a np.ndarray and clears the buffer
    :return: data: row data
    :rtype: np.ndarray
    """

    global raw_data
    data = np.array(raw_data)
    raw_data = [[] for _ in range(number_channels)]
    return data


def create_event_type_array() -> np.ndarray:
    """
    Converts the buffer with the event types to a np.ndarray and clears the buffer
    :return: et: event types
    :rtype: np.ndarray
    """

    global event_type
    et = np.array(event_type)
    event_type.clear()
    return et


def create_position_array() -> np.ndarray:
    """
    Converts the buffer with the positions of the events to a np.ndarray and clears the buffer
    :return: pos: position of the events
    :rtype: np.ndarray
    """

    global event_pos
    pos = np.array(event_pos)
    event_pos.clear()
    return pos


def create_duration_array() -> np.ndarray:
    """
    Converts the buffer with the durations of the events to a np.ndarray and clears the buffer
    :return: duration: duration of the events
    :rtype: np.ndarray
    """

    global event_duration
    duration = np.array(event_duration)
    event_duration.clear()
    return duration


def save_session(metadata: np.ndarray, npz_name: str):
    """
    Save the metadata, the raw data, the event types and the position of the events of one session in a npz-file
    :param np.ndarray metadata: metadata of the session in a np.ndarray
    :param str npz_name: name of the npz-file, not the path name!
    :return: None
    """

    from os.path import dirname, abspath, join
    file_path = join(dirname(dirname(abspath(__file__))), "session", npz_name)

    np.savez(file_path, meta=metadata, raw_data=create_raw_data_array(), event_type=create_event_type_array(),
             event_pos=create_position_array(), event_duration=create_duration_array())
