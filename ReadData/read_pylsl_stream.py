from pylsl import StreamInlet, resolve_byprop

window_size = 125               # size of sliding window in amount of samples, *8ms for time
offset = 12                     # size of offset in amount of samples, *8ms for time

max_time_search_stream = 10     # in s
bool_recover = True             # Setting if the script should terminate or try to recover if  it lost the stream
filter_type = 'type'            # Setting if search by type or name
filter_title = 'EEG'            # Title of the stream

data = []


def read():
    print("looking for an EEG stream...")
    streams = []
    bool_stream = True

    # Search for Stream
    try:
        streams = resolve_byprop(filter_type, filter_title, timeout=max_time_search_stream)
    except:
        print("Exception by searching for streams")
        bool_stream = False

    # create a new inlet to read from the stream
    if len(streams) > 0:
        try:
            inlet = StreamInlet(streams[0], recover=bool_recover)
            print("EEG stream started")
        except:
            print("Exception by StreamInlet")
            bool_stream = False
    else:
        bool_stream = False
        print('Stream not found')

    if bool_stream:
        bool_read = True
        bool_start = True
        offset_data = []
        pushed_elements_count = 0  # counts the samples which are pushed into data from one chunk

        # fill the first window
        while bool_start:
            try:
                chunk, timestamp = inlet.pull_chunk()
            except:
                print('lost stream')
                bool_start = False
                bool_read = False
            if chunk:
                pushed_elements_count = 0
                # print(chunk)
                for sample in chunk:
                    # print(sample)
                    data.append(sample)
                    pushed_elements_count += 1
                    if window_size == len(data):
                        bool_start = False
                    break
        print('first window ready  window size = ', len(data))
        # ToDo call Algorithm with data and offset

        # handle rest of samples in  the chunk
        for i in range(len(chunk)):
            if i >= pushed_elements_count:
                offset_data.append(chunk[i])

        # gather data for the offset
        while bool_read:
            # get chunks of samples
            try:
                chunk, timestamp = inlet.pull_chunk()
            except:
                bool_read = False
                print('lost stream')
            if chunk:
                # print(chunk);
                for sample in chunk:
                    # print(sample)
                    offset_data.append(sample)
                    if len(offset_data) == offset:
                        create_sliding_window(offset_data)
                        # print(offset_data)
                        offset_data.clear()

        inlet.close_stream()


# fill new offset in the sliding window and shift the oldest offset out
# offset_data array with the eeg data;
def create_sliding_window(offset_data):
    for i in range(offset):
        data.append(offset_data[i])

    for i in range(offset):
        data.pop(0)

    # ToDo call Algorithm with data and offset

    print('next window ready   window size = ', len(data))
    # print (data)
    # print(data[0])
    # print(data[offset])


read()
