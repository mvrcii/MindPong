import argparse
import time
import numpy as np

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


def main():
    BoardShim.enable_dev_board_logger()


    params = BrainFlowInputParams()
    params.serial_port = 'COM3'
    count = 0
    board = BoardShim(brainflow.board_shim.BoardIds.CYTON_DAISY_BOARD, params)
    before = time.time()
    board.prepare_session()
    board.start_stream()

    while count < 50:
        data = board.get_board_data()  # get all data and remove it from internal buffer
        after = time.time()
        if np.any(data):
            print(after - before)
            before = after
            print(data, len(data))
            print(count)
            count = 0
        else:
            count += 1
        time.sleep(0.001)

    board.stop_stream()
    board.release_session()




if __name__ == "__main__":
    main()