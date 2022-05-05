import time
from enum import Enum

import brainflow
import numpy as np
from brainflow import BoardShim


""" Skript for buffering the raw data, the trials and saving them as an npz file"""

class Labels(Enum):
    """An Enum Class for different trial labels for event types"""
    INVALID = 99
    LEFT = 0
    RIGHT = 1
    CALIBRATION = 2


NUMBER_CHANNELS = len(BoardShim.get_eeg_channels(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD))

# time which is needed for one sample in s, T = 1/f = 1/125 = 0.008
TIME_FOR_ONE_SAMPLE = 1 / BoardShim.get_sampling_rate(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)

raw_data = [[] for _ in range(NUMBER_CHANNELS)]
event_type = []  # label of a Trial
event_pos = []  # starting position of a Trial
event_duration = []  # duration of a trial in samples
start_time = time.time()
count_trials = 0
count_event_types = 0


def send_raw_data(data, start: time.time() = None):
    """
    Start time of the session is passed only at the first data transfer of the session
    (1) If start is not None the time stamp of the start of session get saved in start_time
    (2) Sent data get saved in raw_data
    :param data[] data: raw data from the data acquisition
    :param time.time() start: time stamp of the start of the session
    """
    if start is not None:
        global start_time
        start_time = start
    for i in range(len(raw_data)):
        raw_data[i].append(data[i][0])


def mark_trial(start: float, end: float, label: Labels):
    """
    (1) Calculation of the trial position in raw_data
    (2) Calculation of the duration of the trial
    (3) Saves the duration of the trial in event_duration
    (4) Saves the label of the trial in event_type
    (5) Saves the trial position in event_pos
    :param time.time() start: time stamp of the start of the trial
    :param time.time() end: time stamp of the end of the trial
    :param Labels label: event_type of the trial
    """
    global start_time, count_trials, count_event_types
    pos = round((start - start_time) / TIME_FOR_ONE_SAMPLE)
    duration = round((end - start) / TIME_FOR_ONE_SAMPLE)
    event_duration.append(duration)
    if label not in event_type:
        count_event_types += 1
    event_type.append(label)
    event_pos.append(pos)
    count_trials += 1
    print("Start-Time: ", start, "End-Time: ", end, "Label: ", label.name)
    print("Finished storing")


def create_raw_data_array() -> np.ndarray:
    """
    Converts the buffer with the trials to a np.ndarray
    :return: np.ndarray data: row data
    """

    data = np.array(raw_data)
    return data


def create_event_type_array() -> np.ndarray:
    """
    Converts the buffer with the event types to a np.ndarray
    :return: np.ndarray et: event types
    """

    et = np.array(event_type)
    return et


def create_position_array() -> np.ndarray:
    """
    Converts the buffer with the positions of the events to a np.ndarray
    :return: np.ndarray pos: position of the events
    """

    pos = np.array(event_pos)
    return pos


def create_duration_array() -> np.ndarray:
    """
    Converts the buffer with the durations of the events to a np.ndarray
    :return: np.ndarray duration: duration of the events
    """

    duration = np.array(event_duration)
    return duration


def save_session(metadata: np.ndarray, npz_name: str):
    """
    Save the metadata, the raw data, the event types, the position and the duration
    of the events of one session in a npz-file
    :param np.ndarray metadata: metadata of the session in a np.ndarray
    :param str npz_name: name of the npz-file, not the path name!
    """
    from os.path import dirname, abspath, join
    file_path = join(dirname(dirname(abspath(__file__))), "session", npz_name)
    np.savez(file_path, meta=metadata, raw_data=create_raw_data_array(), event_type=create_event_type_array(),
             event_pos=create_position_array(), event_duration=create_duration_array())
    reset_data()


def reset_data():
    """Set the counters count_trials and count_event_types to zero  and clears all buffers"""
    global count_trials, count_event_types, event_duration, event_pos, event_type, raw_data
    count_trials = 0
    count_event_types = 0
    event_duration.clear()
    event_pos.clear()
    event_type.clear()
    raw_data = [[] for _ in range(NUMBER_CHANNELS)]
