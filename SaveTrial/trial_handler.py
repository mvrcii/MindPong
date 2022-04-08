import numpy as np
import Labels


raw_data = [[] for _ in range(16)]
event_type = []
event_pos = []
event_duration = []


def save_trial(trial: np.ndarray, junk: np.ndarray, label: Labels):
    """
    (1) Saves duration of the trials in event_pos
    (2) Saves the trial data and junk data in raw_data
    (3) Saves the event type in event_type
    (4) Saves the position of the trials in event_pos
    :param trial: trial data
    :type trial: np.ndarray (16xn)
    :param label: label of the trial
    """
    pos = len(raw_data[0]) + len(junk[0])
    event_duration.append(len(trial[0]))
    for i in range(len(raw_data)):
        raw_data[i].extend(junk[i])
        raw_data[i].extend(trial[i])
    event_type.append(label)
    event_pos.append(pos)

def create_raw_data_array()-> np.ndarray:
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


