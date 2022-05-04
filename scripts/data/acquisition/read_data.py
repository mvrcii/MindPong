import queue
import threading
import platform
import time
import numpy as np
from numpy_ringbuffer import RingBuffer

import serial
import serial.tools.list_ports
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BrainFlowError

from scripts.data.loader.game_dataset_loader import get_channel_rawdata
from scripts.data.visualisation.liveplot_matlab import connect_queue, remove_all_plots, initial_draw
from scripts.mvc.models import ConfigData
from scripts.data.extraction import trial_handler
import scripts.config as config


class QueueManager:
    def __init__(self):
        self.queue_label = queue.Queue(100)
        self.queue_clabel = queue.Queue(100)

        self.queue_c3_pow = queue.Queue(100)
        self.queue_c4_pow = queue.Queue(100)

        self.queue_hcon = queue.Queue(100)
        self.queue_hcon_norm = queue.Queue(100)

    def clear_all_queues(self):
        self.queue_label.queue.clear()
        self.queue_clabel.queue.clear()
        self.queue_c3_pow.queue.clear()
        self.queue_c4_pow.queue.clear()
        self.queue_hcon.queue.clear()
        self.queue_hcon_norm.queue.clear()


# constants
live_Data = True  # boolean to replay a recorded session with session_file_name as file name
session_file_name = 'session-1-01052022-091646.npz'

SAMPLING_RATE = BoardShim.get_sampling_rate(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD) if live_Data else 125

# time which is needed for one sample in s, T = 1/f = 1/125 = 0.008
TIME_FOR_ONE_SAMPLE = 1 / SAMPLING_RATE

SLIDING_WINDOW_DURATION: float  # size of sliding window in s
# size of sliding window in amount of samples, *8ms for time
SLIDING_WINDOW_SAMPLES: int

OFFSET_DURATION: float  # size of offset in s between two consecutive sliding windows
OFFSET_SAMPLES: int  # size of offset in amount of samples, *8ms for time

NUMBER_CHANNELS = len(BoardShim.get_eeg_channels(
    brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)) if live_Data else len(
    ['C3', 'Cz', 'C4', 'P3', 'P4', 'T3', 'F3', 'F4', 'T4'])

# global variables
allow_window_creation = True
first_window = True
first_data = True
stream_available = False  # indicates if stream is available

board: BoardShim
window_buffer: RingBuffer
data_model: ConfigData
queue_manager = QueueManager()


def connect_queues():
    queue_manager.clear_all_queues()
    remove_all_plots()
    connect_queue(queue_manager.queue_c3_pow, 'pow', color='#0096db', row=3, column=1, position=1, name='C3 pow')
    connect_queue(queue_manager.queue_c4_pow, 'pow', color='#009d6b', row=3, column=1, position=1, name='C4 pow')
    connect_queue(queue_manager.queue_hcon, 'hcon', color='#f17a2c', row=3, column=1, position=2, name='hcon')
    connect_queue(queue_manager.queue_hcon_norm, 'hcon', color='#FFC107', row=3, column=1, position=2,
                  name='hcon normalized')
    connect_queue(queue_manager.queue_clabel, 'label', color='#96669e', row=3, column=1, position=3,
                  y_labels=['n', 'l', 'r'], name='calculated label')
    initial_draw()


def init(data_mdl):
    """
    --- starting point ---
    Initializing steps:
    (1) initialize the board
    (2) search for the serial port
    (3) starts the data acquisition
    """
    connect_queues()
    global data_model, first_window
    data_model = data_mdl
    first_window = True

    global SLIDING_WINDOW_DURATION, SLIDING_WINDOW_SAMPLES, OFFSET_DURATION, OFFSET_SAMPLES, TIME_FOR_ONE_SAMPLE, window_buffer, NUMBER_CHANNELS
    SLIDING_WINDOW_DURATION = data_model.window_size / 1000
    SLIDING_WINDOW_SAMPLES = int(SLIDING_WINDOW_DURATION / TIME_FOR_ONE_SAMPLE)
    OFFSET_DURATION = data_model.window_offset / 1000
    OFFSET_SAMPLES = int(OFFSET_DURATION / TIME_FOR_ONE_SAMPLE)
    window_buffer = [RingBuffer(capacity=SLIDING_WINDOW_SAMPLES, dtype=float) for _ in range(NUMBER_CHANNELS)]

    if live_Data:
        params = BrainFlowInputParams()
        params.serial_port = search_port()

        """"
        while not scripts.data.visualisation.liveplot.is_window_ready:
            # wait until plot window is initialized
            time.sleep(0.05)
        
        connect_queues()
        """

        if params.serial_port is not None:
            # BoardShim.enable_dev_board_logger()
            global board, stream_available
            board = BoardShim(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD, params)
            try:
                board.prepare_session()
                board.start_stream()
                stream_available = True
                handle_samples()
            except BrainFlowError as err:
                print(err.args[0])

        else:
            print('Port not found')
    else:
        path = '../scripts/data/session/' + session_file_name
        chan_labels = ['C3', 'Cz', 'C4', 'P3', 'P4', 'T3', 'F3', 'F4', 'T4']
        chan_data, label_data = get_channel_rawdata(session_path=path, ch_names=chan_labels)
        stream_available = True
        handle_samples(chan_data)


def search_port():
    """
    Search for the name of the used usb port and return it
    Returns None if no usb port was found
    :return: str port_name: name of the used serial port
    """

    print('Search...')
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports:
        if port.vid == 1027 and port.pid == 24597:
            port_name = port.device
            print('found port: ', port_name)

            # If operating system is Linux set the Latency of the USB-Port to 1ms
            if platform.system() == 'Linux':
                import os
                set_latency_cmd = 'setserial ' + port_name + ' low_latency'
                os.system(set_latency_cmd)
                get_latency_cmd = 'cat /sys/bus/usb-serial/devices/' + port_name[5:] + '/latency_timer'
                print('set latency timer to: ' + os.popen(get_latency_cmd).read().strip() + 'ms')

            return port_name
    print("Ended Search")
    return None


def handle_samples(chan_data=None):
    """
    Reads EEG data from port, sends it to trial_handler and writes into in the window_buffer
    :param float[] chan_data: raw data from recorded Sessions
    """
    global first_window, window_buffer, allow_window_creation, first_data
    count_samples = 0
    sample_index = 0

    while stream_available and (live_Data or len(chan_data[0]) > sample_index):
        if chan_data is not None:
            data = np.ndarray((len(chan_data), 1))
            for channel_index, samples in enumerate(chan_data[:, sample_index]):
                data[channel_index, 0] = samples
            sample_index += 1
            time.sleep(0.008)
        else:
            data = board.get_board_data(1)[board.get_eeg_channels(
                brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)]  # get all data and remove it from internal buffer
            if len(data[0]) > 0:
                # filter data
                for channel in range(NUMBER_CHANNELS):
                    brainflow.DataFilter.perform_bandstop(data[channel], SAMPLING_RATE, 0.0, 50.0, 5,
                                                          brainflow.FilterTypes.BUTTERWORTH.value, 0)
            else:
                continue
            # only sends trial_handler raw data if trial recording is wished
        if data_model.trial_recording:
            if first_data:
                trial_handler.NUMBER_CHANNELS = NUMBER_CHANNELS
                trial_handler.raw_data = [[] for _ in range(NUMBER_CHANNELS)]
                trial_handler.send_raw_data(data, start=time.time())
                first_data = False
            else:
                trial_handler.send_raw_data(data)
        if allow_window_creation:
            for samples in range(len(data)):
                window_buffer[samples].extend(data[samples])
            count_samples += 1
            if first_window and count_samples == SLIDING_WINDOW_SAMPLES:
                first_window = False
                send_window()
                count_samples = 0
            elif not first_window and count_samples == OFFSET_SAMPLES:
                send_window()
                count_samples = 0
    stop_stream()


def sort_channels(sliding_window, used_ch_names):
    """Filters and sorts the data channels for the algorithm"""
    filtered_sliding_window = list()
    filtered_channel_names = list()
    for i in range(len(used_ch_names)):
        if config.CH_NAMES_WEIGHT[i] != 0:
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


def send_window():
    """Create sliding window and send it to the algorithm"""
    global window_buffer, NUMBER_CHANNELS
    window = np.zeros((NUMBER_CHANNELS, SLIDING_WINDOW_SAMPLES), dtype=float)
    for i in range(len(window)):
        window[i] = np.array(window_buffer[i])
    # sort channels for laplacian calculation
    if live_Data:
        window, used_channels = sort_channels(window, config.BCI_CHANNELS)
    else:
        used_channels = ['C3', 'Cz', 'C4', 'P3', 'P4', 'T3', 'F3', 'F4', 'T4']
    # push window to cursor control algorithm
    # TODO: change OFFSET_DURATION to percentage? Else change calculation in coc algorithm
    from scripts.algorithms.cursor_online_control import perform_algorithm
    perform_algorithm(window, used_channels, SAMPLING_RATE, queue_manager,
                      offset_in_percentage=OFFSET_DURATION / SLIDING_WINDOW_DURATION, data_mdl=data_model)


def stop_stream():
    """Stops the data stream and the releases session"""
    global stream_available
    stream_available = False
    if live_Data and 'board' in globals():
            board.stop_stream()
            board.release_session()


if __name__ == '__main__':
    print('read_data main started ...')
    threading.Thread(target=init, daemon=True).start()
