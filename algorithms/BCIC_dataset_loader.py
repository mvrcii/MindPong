import os
from typing import List
import mne
import numpy as np
from pathlib import Path



CHANNELS = [
            'Fz', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'C5',
            'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'CP3',
            'CP1', 'CPz', 'CP2', 'CP4', 'P1', 'Pz', 'P2',
            'POz']
SAMPLERATE = 250
TMIN = -2
TMAX = 5.5
path = 'BCIC_dataset'
NOTCH_FILTER_FREQ: float = 50


def to_idxs_of_list_str(elements: List[str], list: List[str]):
    """
    Returns list of elements' indexes in string List
    """
    list_upper = [e.upper() for e in list]
    return [list_upper.index(el.upper()) for el in elements]


def calc_n_samples(tmin: float, tmax: float, samplerate: float):
    n_samples = int(round((tmax - tmin) * samplerate))
    return n_samples


def get_subject_fname(subject: int, training: int = 1):
    if training == 1 and (subject == 3 or subject == 7):
        abs_path = Path(path)
        abs_parent_path = abs_path.parent.absolute().parent
        return abs_parent_path.joinpath(path + '/A0' + str(subject) + 'T.npz')
    else:
        print('Error: Illegal parameter')
        raise NotImplementedError


def BP_notch_filtering(data: np.ndarray):
    """
    Optionally executes bandpass and/or notch filtering of given EEG Data if necessary.
    Should be done BEFORE trial extraction!
    :param data: original EEG Data Array
    :return: resampled and/or filtered EEG Data (Sample rate = CONFIG.SYSTEM_SAMPLE_RATE)
    """

    # optional Notch Filter to filter out Powerline Noise
    data = mne.filter.notch_filter(data, Fs=SAMPLERATE, freqs=NOTCH_FILTER_FREQ,
                                   filter_length='auto', phase='zero')
    return data


def get_channel_rawdata(subject: int, n_class: int = 4, ch_names: List[str] = CHANNELS, training: int = 1):
    """
    get raw data of one channel of a subject
    """
    ch_idxs = to_idxs_of_list_str(ch_names, CHANNELS)
    n_trials_max = 6 * 12 * n_class  # 6 runs with 12 trials per class
    n_samples = calc_n_samples(TMIN, TMAX, SAMPLERATE)
    fname = get_subject_fname(subject, training)

    # print('  - Load data of subject %d from file: %s' % (subject, fname))
    data = np.load(fname)

    raw = data['s'].T
    chan_data = raw[ch_idxs, :]
    events_type = data['etyp'].T
    events_position = data['epos'].T
    events_duration = data['edur'].T
    artifacts = data['artifacts'].T

    chan_data = BP_notch_filtering(chan_data)  # Optional bandpass and notch filtering

    # create labels channel
    n_events = events_type.shape[1]
    chan_label = np.full((chan_data.shape[1]), fill_value=-1, dtype=int)
    for i in range(n_events - 1):
        if events_type[0, i] == 769 or events_type[0, i] == 770:
            ind = events_position[0, i]
            while ind < events_position[0, i] + 1000:  # 1000 -> 4 s active trial
                # Left hand          0
                # Right hand         1
                # Both feet          2
                # Tongue             3
                # Unknown            -1
                chan_label[ind] = events_type[0, i] - 769
                ind = ind + 1

    return chan_data, chan_label
