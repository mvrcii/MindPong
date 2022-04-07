import sys
import threading, queue
import time
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import cursor_online_control
import BCIC_dataset_loader as bdl

# GLOBAL DATA
TMIN = 700.0  # Minimum time value shown in the following figures
TMAX = 850.0  # Maximum time value shown in the following figures
TS_SIZE = 1.0  # 1 s time slice
TS_STEP = 0.2  # 50 ms
SAMPLING_RATE = 250
num_used_channels = 0
mutex = threading.Lock
QUEUE_DATA = queue.Queue(300)
QUEUE_LABEL = queue.Queue(300)
SLIDING_WINDOW_SIZE_FACTOR = 5
VALID_VALUES_BORDER = 0.3
'''
Sliding window size: 
    1 -> 200ms
    2 -> 400ms
    ...
    5 -> 1s
'''


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))
        self.data = [0] * 100
        self.label = [0] * 100

        self.graphWidget.setBackground('k')
        self.graphWidget.showGrid(x=True, y=True)

        pen_data = pg.mkPen(width=5, color=(255, 0, 255))
        pen_label = pg.mkPen(width=5, color=(255, 255, 0))

        self.data_line_data = self.graphWidget.plot(self.x, self.data, pen=pen_data)
        self.data_line_label = self.graphWidget.plot(self.x, self.label, pen=pen_label)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        """
        Periodically called to update the values by extracting the current values from the queues.
        """
        try:
            global QUEUE_DATA, QUEUE_LABEL
            # update x value
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

            # update data value
            self.data = self.data[1:]  # Get and remove the first element of the queue
            self.data.append(QUEUE_DATA.get())
            self.data_line_data.setData(self.x, self.data)  # Update the data.

            # update label value
            self.label = self.label[1:]  # Get and remove the first element of the queue
            self.label.append(QUEUE_LABEL.get())
            self.data_line_label.setData(self.x, self.label)  # Update the data.
        except:
            time.sleep(0.005)


def loadBCICDataset(ch_weight):
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

    return chan_data, label_data


def test_algorithm(chan_data, label_data):
    """
    - create overlapping sliding windows
    - Calls the cursor control algorithm
    - calculate und plot accuracy
    :return: None
    """
    accuracy = 0
    global VALID_VALUES_BORDER
    threshold = VALID_VALUES_BORDER
    num_valid_sliding_windows = 0
    n_slices = int((TMAX - TMIN - TS_SIZE) / TS_STEP)
    toff = np.zeros(n_slices, dtype=float)
    label = np.zeros(n_slices, dtype=int)
    norm_hcon = np.zeros(n_slices, dtype=float)
    for i in range(n_slices):
        toff[i] = TMIN + i * TS_STEP
        label[i] = label_data[int((TMIN + i * TS_STEP) * SAMPLING_RATE)]
        start_idx = int(toff[i] * SAMPLING_RATE)
        stop_idx = int(((toff[i] + TS_SIZE) * SAMPLING_RATE) - 1)

        # calls the one and only cursor control algorithm
        normalized_hcon = cursor_online_control.perform_algorithm(chan_data[:, start_idx:stop_idx],
                                                                  SLIDING_WINDOW_SIZE_FACTOR)
        norm_hcon[i] = normalized_hcon

        # converts the returned hcon to the corresponding label
        if normalized_hcon > threshold:
            calculated_label = 0
        elif normalized_hcon < -threshold:
            calculated_label = 1
        else:
            calculated_label = -1

        try:
            global QUEUE_DATA, QUEUE_LABEL
            QUEUE_DATA.put(normalized_hcon)
            QUEUE_LABEL.put(label[i])
        except:
            print('Fehler: kann nicht reingeldaden werden')

        # TODO: compare the calculated label with the predefined label, if same -> increase accuracy

    # calculate und plot accuracy
    # accuracy /= num_valid_sliding_windows
    # print(f'Accuracy = {accuracy}')


def start_algorithm():
    #                 Fz  FC3  FC1  FCz  FC2  FC4  C5  C3  C1  Cz  C2  C4  C6  CP3  CP1  CPz  CP2  CP4  P1  Pz  P2  POz
    ch_names_weight = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
    preloaded_data, preloaded_labels = loadBCICDataset(ch_names_weight)
    test_algorithm(preloaded_data, preloaded_labels)


if __name__ == '__main__':
    threading.Thread(target=start_algorithm).start()

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.showFullScreen()
    w.show()
    sys.exit(app.exec_())
