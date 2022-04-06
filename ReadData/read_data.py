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

bool_stream = False  # indicates if stream is available
board: BoardShim
buffer = [RingBuffer(capacity=10 * 125, dtype=float) for x in range(16)]


def init():
    """
    --- starting point ---
    Initializing steps:
    (1) initialize the board
    (2) search for the serial port
    (3) starts the data acquisition
    """
    params = BrainFlowInputParams()
    params.serial_port = search_port()

    if params.serial_port is not None:
        BoardShim.enable_dev_board_logger()
        global board, bool_stream
        board = BoardShim(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD, params)
        board.prepare_session()
        board.start_stream()
        bool_stream = True
        handle_samples()
    else:
        print('Port not found')


def search_port():
    """
    Search for the name of the used usb port
    :return: name of the used serial port
    :rtype: str
    """
    port_name = None
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
    Reads EEG data from port and writes into in the ringbuffer
    """
    while bool_stream:
        data = board.get_board_data(1)[board.get_eeg_channels(
            brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD)]  # get all data and remove it from internal buffer
        if len(data[0]) > 0:
            for i in range(len(data)):
                buffer[i].append(data[i][0])


def get_trial_data(duration_in_ms: int) -> np.ndarray:
    """
    Get the latest EGG data from the ringbuffer which was recorded in the last duration_in_ms milliseconds.

    :param duration_in_ms: in ms, time span in which the required EGG data was collected
    :type duration_in_ms: int
    :return: two dimensional ndarray with the required EGG data
    :rtype: np.ndarray
    :raises  Throws IndexError if not enough data is in the buffer for the given duration
    """
    copied_buffer = copy.deepcopy(buffer)
    duration_in_samples = int(duration_in_ms / (time_for_one_sample * 1000))
    i = len(copied_buffer[0]) - duration_in_samples
    #The requested trial duration exceeds the buffer size
    if i < 0:
        print('not enough data')
        raise IndexError('Duration to long!')
    trial_data = [[] for x in range(16)]
    for x in range(16):
        trial_data[x] = np.array(copied_buffer[x][i:])
    return np.array(trial_data)


def stop_stream():
    """
    Stops the data stream and the releases session
    """
    global bool_stream
    bool_stream = False
    time.sleep(1)
    board.stop_stream()
    board.release_session()


init()
