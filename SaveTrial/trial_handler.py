import numpy as np


trial_buffer = [[] for x in range(16)]
event_type = []
position = []


def save_trial(trial: np.ndarray, label):
    """
    save the trials in a buffer
    :param trial: trial data
    :type trial: np.ndarray (16xn)
    """
    pos = len(trial_buffer[0])
    for i in range(len(trial_buffer)):
        trial_buffer[i].extend(trial[i])
    event_type.append(label)
    position.append(pos)

def create_raw_data_array()-> np.ndarray:
    """
    Converts the buffer with the trials to a np.ndarray and clears the buffer afterwards
    :return: raw data in a np.ndarray
    """
    global trial_buffer
    return np.array(trial_buffer)

def create_event_type_array()-> np.ndarray:
    global event_type
    return np.array(event_type)

def create_position_array() -> np.ndarray:
    global position
    return np.array(position)

def save_session(metadata: np.ndarray, npy_name: str):
    name = '../Session/'+npy_name
    print(name)
    np.savez(name, meta=metadata, raw_data=create_raw_data_array(), event_type=create_event_type_array(),
             positon=create_position_array())


