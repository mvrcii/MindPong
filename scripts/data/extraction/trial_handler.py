import time
from enum import Enum

import brainflow
import numpy as np
from brainflow import BoardShim


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
event_type = []
event_pos = []
event_duration = []
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
    for i in raw_data:
        print(i[pos:pos+duration])


def create_raw_data_array() -> np.ndarray:
    """
    Converts the buffer with the trials to a np.ndarray and clears the buffer
    :return: np.ndarray data: row data
    """

    global raw_data
    data = np.array(raw_data)
    raw_data = [[] for _ in range(NUMBER_CHANNELS)]
    return data


def create_event_type_array() -> np.ndarray:
    """
    Converts the buffer with the event types to a np.ndarray and clears the buffer
    :return: np.ndarray et: event types
    """

    global event_type
    et = np.array(event_type)
    event_type.clear()
    return et


def create_position_array() -> np.ndarray:
    """
    Converts the buffer with the positions of the events to a np.ndarray and clears the buffer
    :return: np.ndarray pos: position of the events
    """

    global event_pos
    pos = np.array(event_pos)
    event_pos.clear()
    return pos


def create_duration_array() -> np.ndarray:
    """
    Converts the buffer with the durations of the events to a np.ndarray and clears the buffer
    :return: np.ndarray duration: duration of the events
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
    """

    from os.path import dirname, abspath, join
    file_path = join(dirname(dirname(abspath(__file__))), "session", npz_name)
    np.savez(file_path, meta=metadata, raw_data=create_raw_data_array(), event_type=create_event_type_array(),
             event_pos=create_position_array(), event_duration=create_duration_array())
    reset_counters()


def reset_counters():
    """Set the counters count_trials and count_event_types to zero"""
    global count_trials, count_event_types
    count_trials = 0
    count_event_types = 0
