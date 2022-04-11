import numpy as np

from SaveTrial.Labels import Labels

trial_buffer = [[] for _ in range(16)]
event_type = []
position = []


def save_trial(trial: np.ndarray, label: Labels):
    """
    save the trials in a buffer
    :param trial: trial data
    :type trial: np.ndarray (16xn)
    :param label: label of the trial
    """
    pos = len(trial_buffer[0])
    for i in range(len(trial_buffer)):
        trial_buffer[i].extend(trial[i])
    event_type.append(label)
    position.append(pos)


def create_raw_data_array() -> np.ndarray:
    """
    Converts the buffer with the trials to a np.ndarray and clears the buffer
    :return: raw data in a np.ndarray
    """
    global trial_buffer
    raw_data = np.array(trial_buffer)
    trial_buffer = [[] for _ in range(16)]
    return raw_data


def create_event_type_array() -> np.ndarray:
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
    global position
    pos = np.array(position)
    position.clear()
    return pos


def save_session(metadata: np.ndarray, npz_name: str):
    """
    Save the metadata, the raw data, the event types and the position of the events of one session in a npz-file
    :param metadata: metadata of the session in a np.ndarray
    :param npz_name: name of the npz-file, not the path name!
    """
    name = '../Session/' + npz_name
    print(name)
    np.savez(name, meta=metadata, raw_data=create_raw_data_array(), event_type=create_event_type_array(),
             position=create_position_array())
