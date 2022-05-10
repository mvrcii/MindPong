import threading, queue
import time
import matplotlib.pyplot as plt
import numpy as np
from tests.data.analysis import BCIC_dataset_loader as bdl
from scripts.data.analysis import cursor_control_algorithm
import scripts.data.visualisation.liveplot_matlab as liveplot_matplot

# constants
TMIN = 100.0  # Minimum time value shown in the following figures
TMAX = 850.0  # Maximum time value shown in the following figures

# GLOBAL DATA
num_used_channels = 0
mutex = threading.Lock


class ConfigData:
    def __init__(self):
        self.threshold = 1.5
        self.f_min = 8
        self.f_max = 12
        self.window_size = 1.0
        self.window_offset = 0.05
        self.offset_in_percentage = self.window_size / self.window_offset / 100.0
        self.sampling_rate = 250
        self.draw_plot = True


class QueueManager:
    def __init__(self):
        self.queue_label = queue.Queue(100)
        self.queue_clabel = queue.Queue(100)

        self.queue_c3 = queue.Queue(100)
        self.queue_c4 = queue.Queue(100)

        self.queue_c3_pow = queue.Queue(100)
        self.queue_c4_pow = queue.Queue(100)

        self.queue_hcon = queue.Queue(100)
        self.queue_hcon_stand = queue.Queue(100)


def load_bcic_dataset(ch_weight):
    """
    - converts ch_weight into the corresponding channels and inserts C3 and C4 to the first two places in the list
    - provides the BCIC dataset for further processing
    :param ch_weight: weighted array to set channel selection
    :return: loaded_data: contains the samples of all channels
                Structure of 2-dim array from the data loader:
                        dim 0: EEG channel
                        dim 1: sample
             loaded_labels: contains the corresponding label for each trial
    """
    # Load BCIC dataset
    used_ch_names = []
    # map ch_weight(channel selection) with channels names in BCI dataset to load to selected channels
    for i in range(len(bdl.CHANNELS)):
        if ch_weight[i] != 0:
            if bdl.CHANNELS[i] == 'C3':
                used_ch_names.insert(0, bdl.CHANNELS[i])
            elif bdl.CHANNELS[i] == 'C4':
                used_ch_names.insert(1, bdl.CHANNELS[i])
            else:
                used_ch_names.append(bdl.CHANNELS[i])
    global num_used_channels
    num_used_channels = len(used_ch_names)

    chan_data, label_data = bdl.get_channel_rawdata(subject=7, n_class=2, ch_names=used_ch_names)

    return chan_data, label_data, used_ch_names


def test_algorithm(chan_data, label_data, used_ch_names):
    """
    - create overlapping sliding windows
    - Calls the cursor control algorithm
    - calculate und plot accuracy
    :return: None
    """
    config = ConfigData()
    accuracy = 0
    found_label = False
    num_valid_sliding_windows = 0
    n_slices = int((TMAX - TMIN - config.window_size) / config.offset_in_percentage)
    toff = np.zeros(n_slices, dtype=float)
    label = np.zeros(n_slices, dtype=int)
    for i in range(n_slices):
        toff[i] = TMIN + i * config.offset_in_percentage
        label[i] = label_data[int((TMIN + i * config.offset_in_percentage) * config.sampling_rate)]
        start_idx = int(toff[i] * config.sampling_rate)
        stop_idx = int(((toff[i] + config.window_size) * config.sampling_rate) - 1)

        # calls the one and only cursor control algorithm
        calculated_label = cursor_online_control.perform_algorithm(chan_data[:, start_idx:stop_idx], used_ch_names, config.sampling_rate, queue_manager, data_mdl=config, offset_in_percentage=config.offset_in_percentage)

        # compare the calculated label with the predefined label, if same -> increase accuracy
        if label[i] != -1:
            if label[i] == calculated_label:
                found_label = True

        if label[i] != label[i-1]:
            if found_label:
                accuracy += 1

            found_label = False
            num_valid_sliding_windows += 0.5

    # calculate und plot accuracy
    num_valid_sliding_windows = int(num_valid_sliding_windows)
    print(f'accuracy: {accuracy}\nnum_sliding_windows: {num_valid_sliding_windows}')
    accuracy /= num_valid_sliding_windows
    print(f'Accuracy = {accuracy}')


def connect_queues():
    """
    Connects the queues of type queuemanager object which are
    filled in the cursor control algorithm with an object in liveplot_matlab
    in which a reference is stored, so that the queue can be emptied there.
    """
    liveplot_matplot.connect_queue(queue_manager.queue_c3_pow, 'pow', color='#0096db', row=3, column=1, position=1, name='C3 pow')
    liveplot_matplot.connect_queue(queue_manager.queue_c4_pow, 'pow', color='#009d6b', row=3, column=1, position=1, name='C4 pow')
    liveplot_matplot.connect_queue(queue_manager.queue_hcon, 'hcon', color='#f17a2c', row=3, column=1, position=2, name='hcon')
    liveplot_matplot.connect_queue(queue_manager.queue_hcon_stand, 'hcon', color='#FFC107', row=3, column=1, position=2, name='hcon standardized')
    liveplot_matplot.connect_queue(queue_manager.queue_clabel, 'label', color='#96669e', row=3, column=1, position=3, y_labels=['n', 'l', 'r'],name='calculated label')


def sort_incoming_channels(sliding_window, used_ch_names):

    #                 'C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1', 'O2', 'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2', 'CP6'
    ch_names_weight = [1,    0,    1,    0,    0,    0,    0,    0,     1,     1,     1,     1,     1,     1,     1,    1]

    #                 'C3', 'Cz', 'C4', 'P3', '?', 'P4', 'T3', '?', '?', 'F3', 'F4', '?', '?', '?', '?', 'T4'
    ch_names_weight = [1,    1,    1,    1,    0,    1,    1,   0,   0,   1,    1,    0,   0,   0,   0,    1]

    filtered_sliding_window = list()
    filtered_channel_names = list()
    for i in range(len(used_ch_names)):
        if ch_names_weight[i] != 0:
            if used_ch_names[i] == 'C3':
                filtered_channel_names.insert(0, used_ch_names[i])
                filtered_sliding_window.insert(0, sliding_window[i])
            elif used_ch_names[i] == 'C4':
                filtered_channel_names.insert(1, used_ch_names[i])
                filtered_sliding_window.insert(1, sliding_window[i])
            else:
                filtered_channel_names.append(used_ch_names[i])
                filtered_sliding_window.append(sliding_window[i])

    filtered_sliding_window = np.asarray(filtered_sliding_window)
    return filtered_sliding_window, filtered_channel_names


def test_algorithm_with_dataset():
    #                 Fz  FC3  FC1  FCz  FC2  FC4  C5  C3  C1  Cz  C2  C4  C6  CP3  CP1  CPz  CP2  CP4  P1  Pz  P2  POz
    ch_names_weight = [0,  1,   1,   0,   1,   1,   0,  1,  0,  0,  0,  1,  0,  1,   1,   0,   1,   1,   0,  0,  0,  0]
    preloaded_data, preloaded_labels, used_ch_names = load_bcic_dataset(ch_names_weight)
    test_algorithm(preloaded_data, preloaded_labels, used_ch_names)


if __name__ == '__main__':
    print('CCA-test main started ...')
    queue_manager = QueueManager()
    test_algorithm_with_dataset()




