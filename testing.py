import argparse
import time
import platform

import numpy

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds


def main():
    BoardShim.enable_dev_board_logger()

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    """""
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='COM3')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')

    parser.add_argument('--file', type=str, help='file', required=False, default='')
    """
    args = parser.parse_args()

    params = BrainFlowInputParams()
    """" 
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    """

    window_size = 0.010
    time_counter = 0
    start_time = time.time()

    # Assignment of the serial port according to the operating system used
    if platform.system() == 'Windows':
        params.serial_port = 'COM3'
    elif platform.system() == 'Linux':
        params.serial_port = '/dev/ttyUSB*'
    elif platform.system() == 'Darwin':
        params.serial_port = ' '

    board = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    print("Preparing Session")
    board.prepare_session()
    print("Successfully prepared Session")

    print("Start streaming data")
    board.start_stream()

    num_rows = board.get_board_data_count()
    eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD)

    while True:

        # data = board.get_current_board_data(1) # get all data and remove it from internal buffer
        time.sleep(window_size)
        row_now = board.get_board_data_count()
        if num_rows != row_now:
            print(time.time() - start_time)
            num_rows = row_now
            print(row_now)

        # print(passed_time, ": ", data[1])
        """for i in reversed(range(board.get_num_rows(BoardIds.CYTON_DAISY_BOARD))):
            if i not in eeg_channels:
                data = numpy.delete(data, i, 0)
        """

        """for i in range(len(data[0])):
            for j in range(len(data)):
                print(data[j][i])
            print("                                                                            ")
        """
        # print(data)
        # print(board.get_sampling_rate(BoardIds.CYTON_DAISY_BOARD))
        # print(board.get_board_data_count())

        """
        data = board.get_board_data()
        help_array = [0 for x in range(w)]
        for i in BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD):
            help_array[i-1] = data[i][0]
        window.insert(0, help_array)
        window.pop(10)
        print(window)
        """



    else:
        board.stop_stream()
        print("Stop streaming data")
        board.release_session()


if __name__ == "__main__":
    main()
