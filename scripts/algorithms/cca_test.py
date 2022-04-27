import threading, queue
import time

import numpy as np
from scripts.algorithms import cursor_online_control, BCIC_dataset_loader as bdl
import scripts.data.visualisation.liveplot
from scripts.data.visualisation.liveplot_matlab import start_live_plot, connect_queue

# GLOBAL DATA
TMIN = 100.0  # Minimum time value shown in the following figures
TMAX = 850.0  # Maximum time value shown in the following figures
TS_SIZE = 1.0  # 1 s time slice
TS_STEP = 0.2  # 50 ms in percentage
SAMPLING_RATE = 250
num_used_channels = 0
mutex = threading.Lock
SLIDING_WINDOW_SIZE_FACTOR = 5



'''
Sliding window SIZE: 
    1 -> 200ms
    2 -> 400ms
    ...
    5 -> 1s
'''

class QueueManager:
    def __init__(self):
        self.queue_label = queue.Queue(100)
        self.queue_clabel = queue.Queue(100)

        self.queue_c3 = queue.Queue(100)
        self.queue_c4 = queue.Queue(100)

        self.queue_c3_pow = queue.Queue(100)
        self.queue_c4_pow = queue.Queue(100)

        self.queue_hcon = queue.Queue(100)
        self.queue_hcon_norm = queue.Queue(100)


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
    accuracy = 0
    found_label = False
    num_valid_sliding_windows = 0
    n_slices = int((TMAX - TMIN - TS_SIZE) / TS_STEP)
    toff = np.zeros(n_slices, dtype=float)
    label = np.zeros(n_slices, dtype=int)
    for i in range(n_slices):
        toff[i] = TMIN + i * TS_STEP
        label[i] = label_data[int((TMIN + i * TS_STEP) * SAMPLING_RATE)]
        start_idx = int(toff[i] * SAMPLING_RATE)
        stop_idx = int(((toff[i] + TS_SIZE) * SAMPLING_RATE) - 1)

        # calls the one and only cursor control algorithm
        calculated_label = cursor_online_control.perform_algorithm(chan_data[:, start_idx:stop_idx], used_ch_names, SAMPLING_RATE, queue_manager, offset_in_percentage=TS_STEP)
        channel_0 = chan_data[0, start_idx:stop_idx]
        channel_1 = chan_data[1, start_idx:stop_idx]
        for sample in range(len(channel_0)):
            try:
                queue_manager.queue_c3.put(channel_0[sample], True)
                queue_manager.queue_c4.put(channel_1[sample], True)
            except queue.Full:
                print('Queue is full')
            # time.sleep(0.00008)

        # try:
        #     queue_manager.queue_label.put_nowait(label[i])
        # except queue.Full:
        #     pass

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

    # scripts.data.visualisation.liveplot.add_queue(('QUEUE_CLABEL', '#F1C40F', queue_manager.queue_c3_pow))
    # scripts.data.visualisation.liveplot.add_queue(('QUEUE_LABEL', '#16A085', queue_manager.queue_c4_pow))
    # scripts.data.visualisation.liveplot.add_queue(('QUEUE_HCON', '#9B59B6', queue_hcon))
    connect_queue(queue_manager.queue_c3, 'raw', 211)
    connect_queue(queue_manager.queue_c4, 'raw', 211)
    connect_queue(queue_manager.queue_c3_pow, 'pow', 212)
    connect_queue(queue_manager.queue_c4_pow, 'pow', 212)

def sort_incoming_channels(sliding_window, used_ch_names):

    #                 'C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1', 'O2', 'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2', 'CP6'
    ch_names_weight = [1,    0,    1,    0,    0,    0,    0,    0,     1,     1,     1,     1,     1,     1,     1,     1]

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
    connect_queues()
    test_algorithm(preloaded_data, preloaded_labels, used_ch_names)


if __name__ == '__main__':
    print('CCA-test main started ...')
    queue_manager = QueueManager()
    threading.Thread(target=test_algorithm_with_dataset, daemon=True).start()
    # scripts.data.visualisation.liveplot.start_liveplot()
    start_live_plot(queue_manager, 0.00001)

