from pylsl import StreamInlet, resolve_byprop

window_size = 125  # size of sliding window in amount of samples, *8ms for time
offset = 12  # size of offset in amount of samples, *8ms for time
time_for_one_sample = 0.008 #time which is needed for one sample in s

max_time_search_stream = 10  # in s
bool_recover = True  # Setting if the script should terminate or try to recover if  it lost the stream
filter_type = 'type'  # Setting if search by type or name
filter_title = 'EEG'  # Title of the stream

data = []
offset_data = []

""""
converts given parameters in s into amounts of samples, declare the parameters with this function
window_size_sec: sliding window size in s
offset_sec: offset size in s
"""
def set_parameters(window_size_sec, offset_sec):
    window_size = int(window_size_sec/time_for_one_sample)
    offset = int(offset_sec/time_for_one_sample)
    return window_size, offset


# start reading stream
def read_stream():
    print("looking for an EEG stream...")
    bool_stream, inlet = init(stream())
    if bool_stream:
        # fill the first window
        bool_read = read_first(inlet)
        if bool_read:
            read(inlet)


# starts the stream
def init(streams):
    # create a new inlet to read from the stream
    if len(streams) > 0:
        try:
            inlet = StreamInlet(streams[0], recover=bool_recover)
            print("EEG stream started")
            return True, inlet
        except:
            print("Exception by StreamInlet")
            return False, None
    else:
        print('Stream not found')
        return False, None


# search stream
def stream():
    streams = []
    try:
        streams = resolve_byprop(filter_type, filter_title, timeout=max_time_search_stream)
    except:
        print("Exception by searching for streams")
        return None
    return streams


# fill the first window
def read_first(inlet):
    bool_first = True
    while bool_first:
        try:
            chunk, timestamp = inlet.pull_chunk()
        except:
            print('lost stream')
            return False
        if chunk:
            pushed_elements_count = 0
            # print(chunk)
            for sample in chunk:
                # print(sample)
                data.append(sample)
                pushed_elements_count += 1
                if window_size == len(data):
                    bool_first = False
                    break

    print('first window ready  window size = ', len(data))
    # ToDo call Algorithm with data and offset

    # handle rest of samples in  the chunk
    for i in range(len(chunk)):
        if i >= pushed_elements_count:
            offset_data.append(chunk[i])

    return True


# read data from stream
def read(inlet):
    bool_read = True
    # get chunks of samples
    while bool_read:
        try:
            chunk, timestamp = inlet.pull_chunk()
        except:
            bool_read = False
            print('lost stream')
            return False
        if chunk:
            # print(chunk);
            for sample in chunk:
                # print(sample)
                offset_data.append(sample)
                if len(offset_data) == offset:
                    create_sliding_window()
                    # print(offset_data)
                    offset_data.clear()
    inlet.close_stream()


# fill new offset in the sliding window and shift the oldest offset out
# offset_data array with the eeg data;
def create_sliding_window():
    for i in range(offset):
        data.append(offset_data[i])

    for i in range(offset):
        data.pop(0)

    # ToDo call Algorithm with data and offset

    print('next window ready   window size = ', len(data))
    # print (data)
    # print(data[0])
    # print(data[offset])

# read_stream()
