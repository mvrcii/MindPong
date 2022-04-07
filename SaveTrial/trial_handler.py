import numpy as np

buffer = [[] for x in range(16)]


def save_trial(trial: np.ndarray):
    """
    save the trials in a buffer
    :param trial: trial data
    :type trial: np.ndarray (16xn)
    """
    for i in range(len(buffer)):
        buffer[i].extend(trial[i])


def save_session(metadata):
    pass



