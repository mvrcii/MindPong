import numpy as np
from numpy_ringbuffer import RingBuffer
import time
import serial
import serial.tools.list_ports
import copy

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams

# time which is needed for one sample in s, T = 1/f = 1/125 = 0.008
time_for_one_sample = 1 / BoardShim.get_sampling_rate(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)

sliding_window_duration = 0.2  # size of sliding window in s
# size of sliding window in amount of samples, *8ms for time
sliding_window_samples = int(sliding_window_duration / time_for_one_sample)

offset_duration = 0.1  # size of offset in s between two consecutive sliding windows
offset_samples = int(offset_duration / time_for_one_sample)  # size of offset in amount of samples, *8ms for time


allow_window_creation = True
first_window = True
stream_available = False  # indicates if stream is available
board: BoardShim
buffer = [RingBuffer(capacity=10 * 125, dtype=float) for x in range(16)]


def init():
    """
    - start function
    - initialize the board
    - search for the serial port
    - starts the data acquisition
    """
    params = BrainFlowInputParams()
    params.serial_port = search_port()

    if params.serial_port is not None:
        BoardShim.enable_dev_board_logger()
        global board
        board = BoardShim(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD, params)
        board.prepare_session()
        board.start_stream()
        global stream_available
        stream_available = True
        handle_samples()
    else:
        print('Port not found')


def search_port():
    """
    - search for the name of the used usb port
    :return: name of the used serial port
    :rtype: str
    """
    print('Search...')
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports:
        if port.vid == 1027 and port.pid == 24597:
            port_name = port.device
            print('found port: ', port_name)
            return port_name
    return None


def handle_samples():
    """
    - reads data from port and writes it in the ringbuffer
    """
    count = 0
    global first_window
    while stream_available:
        data = board.get_board_data(1)[board.get_eeg_channels(
            brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)]  # get all data and remove it from internal buffer
        if len(data[0]) > 0:
            # ToDo block buffer
            """
            To avoid iconsistence of data because of a call of get_data()
            """
            for i in range(len(data)):
                buffer[i].append(data[i][0])
            count += 1
            if allow_window_creation:
                if (first_window and count == sliding_window_samples) or (not first_window and count == offset_samples):
                    count = 0
                    first_window = False
                    send_window()


def get_trial_data(duration_in_ms: int) -> np.ndarray:
    """
    Get the latest EGG data from the ringbuffer which recorded within the time period duration_in_ms

    :param duration_in_ms: in ms, time span in which the required egg data was collected
    :type duration_in_ms: int
    :return: two dimensional ndarray with the required EEG data
    :rtype: np.ndarray
    :raises Throws IndexError if not enough data is in the buffer for the given duration
    """
    # ToDo block buffer instead of copy
    duration_in_samples = int(duration_in_ms / (time_for_one_sample * 1000))
    return get_data(duration_in_samples)


def get_data(duration_in_samples: int) -> np.ndarray:
    """
        Get the latest EEG data from the ringbuffer which recorded within the time period duration_in_ms

        :param duration_in_samples: in samples, amount of the required samples
        :type  duration_in_samples: int
        :return: two dimensional ndarray with the required EEG data
        :rtype: np.ndarray
        :raises Throws IndexError if not enough data is in the buffer for the given duration
        """
    # ToDo block buffer instead of copy
    copied_buffer = copy.deepcopy(buffer)
    i = len(copied_buffer[0]) - duration_in_samples
    if i < 0:
        print('not enough data')
        raise IndexError('Duration to long!')
    trial_data = [[] for x in range(16)]
    for x in range(16):
        trial_data[x] = np.array(copied_buffer[x][i:])
    return np.array(trial_data)


def send_window():
    """
    Create sliding window and send it to the algorithm
    """
    window = get_data(sliding_window_samples)
    # ToDo: push window to algorithm


def stop_stream():
    """
    -stops data stream and releases session
    """
    global stream_available
    stream_available = False
    time.sleep(1)
    board.stop_stream()
    board.release_session()


init()
