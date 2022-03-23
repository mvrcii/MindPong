import time

import numpy
from pylsl import StreamInlet, resolve_stream

data = []


def read():
    print("looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')
    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    bool_read = True
    valid_samples = 0
    offset = 12  # in count of samples, *8ms for time
    offset_data = []

    while bool_read:
        # get chunks of samples
        chunk, timestamp = inlet.pull_chunk()
        if chunk:
            # print(chunk);
            for sample in chunk:
                # print(sample)
                offset_data.append(sample)
                valid_samples += 1
                if valid_samples == offset:
                    valid_samples = 0
                    create_sliding_window(offset_data, offset)
                    #print(offset_data)
                    offset_data.clear()


def create_sliding_window(offset_data, offset):
    data.append(offset_data)
    print(data)
    print(len(data))


    data.pop(0)


read()
