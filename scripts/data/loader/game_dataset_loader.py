"""
Based on bcic_data_loading.py
Script to read npz files from MindPong and converting them in a Format for the ML-BCI-framework
"""

from typing import List

import mne
import numpy as np

from scripts.config import NOTCH_FILTER_FREQ, NOTCH_FILTER


def bp_notch_filtering(data: np.ndarray, samplerate: int = 125):
    """
    Optionally executes bandpass and/or notch filtering of given EEG Data if necessary.
    Should be done BEFORE trial extraction!
    :param data: original EEG Data Array
    :param samplerate: samplerate of the data
    :return: resampled and/or filtered EEG Data (Sample rate = CONFIG.SYSTEM_SAMPLE_RATE)
    """

    # optional Notch Filter to filter out Powerline Noise
    data = mne.filter.notch_filter(data, Fs=samplerate, freqs=NOTCH_FILTER_FREQ,
                                   filter_length='auto', phase='zero')
    return data


def to_idxs_of_list_str(elements: List[str], list: List[str]):
    """
    :param elements: list of selected channels
    :param list: list of all available channels
    Returns list of elements' indexes in string List
    """
    list_upper = [e.upper() for e in list]
    return [list_upper.index(el.upper()) for el in elements]


def get_channel_rawdata(session_path: str, ch_names: List[str] = None):
    """
    loads the npz file and transforms the data for the ML-BCI framework
    :param session_path: path of the npz file
    :param ch_names: filter for the channels
    :return:
        chan_data: data
        chan_label: labels
    """

    data = np.load(session_path, allow_pickle=True)

    meta = data['meta']
    chan_data = data['raw_data']
    event_type = data['event_type']
    event_pos = data['event_pos']
    event_dur = data['event_duration']

    samplerate = meta[5][1]
    channels = meta[6][1]

    if ch_names:
        # select channels
        try:
            ch_idxs = to_idxs_of_list_str(ch_names, channels)
            chan_data = chan_data[ch_idxs, :]
        except ValueError:
            print('Channel name unknown/not present')
            return None, None

    if NOTCH_FILTER:
        chan_data = bp_notch_filtering(chan_data, samplerate)  # Optional bandpass and notch filtering

    chan_label = np.full(chan_data.shape[0], -1, dtype=int)
    for pos, dur, e_type in zip(event_pos, event_dur, event_type):
        chan_label[pos:pos + dur] = e_type.value
        # Left hand          0
        # Right hand         1
        # Calibration        2
        # Unknown           -1
    return chan_data, chan_label
