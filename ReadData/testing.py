import time

import numpy
from pylsl import StreamInlet, resolve_stream

data = []


def read():
    print("looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')
    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    window_size = 125 # size of sliding window in amount of samples
    bool_read = True
    valid_samples = 0
    offset = 12  # in count of samples, *8ms for time
    offset_data = []
    bool_start = True
    pushed_elements_count = 0 # counts samples which are pushed into data from one chunk
    while bool_start:
        chunk, timestamp = inlet.pull_chunk()
        pushed_elements_count = 0
        if chunk:
            # print(chunk);
            for sample in chunk:
                # print(sample)
                data.append(sample)
                valid_samples += 1
                pushed_elements_count += 1
                if window_size == valid_samples:
                    valid_samples = 0
                    bool_start = False
                break
        #ToDo call Alghorithmus

    #handle rest of samples in  the chunk
    for i in range(len(chunk)):
        if i >= pushed_elements_count:
            offset_data.append(chunk[i])
            valid_samples += 1

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


#fill new offset in the sliding window and shift the oldest offset out
#offset_data array with the eeg data; offset size of the ofset
def create_sliding_window(offset_data, offset):
    for i in range(offset):
        data.append(offset_data[i])

    for i in range(offset):
        data.pop(0)

    #ToDo call Algorithmus

    print(data)
    print(len(data))


read()
