from pylsl import StreamInlet, resolve_byprop

time_for_one_sample = 0.008  # time which is needed for one sample in s, T = 1/f = 1/125 = 0.008

window_size_sec = 0.2  # size of sliding window in s
window_size = int(window_size_sec/time_for_one_sample)  # size of sliding window in amount of samples, *8ms for time

offset_sec = 0.1  # size of offset in s
offset = int(offset_sec/time_for_one_sample)  # size of offset in amount of samples, *8ms for time


max_time_search_stream = 10  # in s, Maximum time until the program stops searching for the stream if none is found
bool_recover = True  # Controls the behavior when the stream is lost:
                     # Attempts to recover stream if true, script termination if false.
filter_type = 'type'  # Setting if search by type or name
filter_title = 'EEG'  # Title of the stream

data = []
offset_data = []

### starting point ###
# start reading the stream
def read_stream():
    print("looking for an EEG stream...")
    bool_stream, inlet = init(stream())
    if bool_stream:
        # fill the first window
        bool_read = read_first_sliding_window(inlet)
        if bool_read:
            read(inlet)



# starts the stream
def init(streams):
    # create a new inlet to read from the stream
    # If multiple streams were found, the first one will be taken
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


# search for streams
def stream():
    streams = []
    try:
        streams = resolve_byprop(filter_type, filter_title, timeout=max_time_search_stream)
    except:
        print("Exception by searching for streams")
        return None
    return streams


# fill the first window
def read_first_sliding_window(inlet):
    sufficient_samples_read = True
    while sufficient_samples_read:
        try:
            chunk, timestamp = inlet.pull_chunk()
        except:
            print('lost stream')
            return False
        if chunk:
            pushed_elements_count = 0
            for sample in chunk:
                data.append(sample)
                pushed_elements_count += 1
                if window_size == len(data):
                    sufficient_samples_read = False
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
            for sample in chunk:
                offset_data.append(sample)
                if len(offset_data) == offset:
                    create_sliding_window()
                    offset_data.clear()
    inlet.close_stream()


# fill new offset in the sliding window and shift the oldest offset out
# offset_data array with the eeg data;
def create_sliding_window():
    for i in range(offset):
        data.append(offset_data[i])
        data.pop(0)



    # ToDo call Algorithm with data and offset

    print('next window ready   window size = ', len(data))


#read_stream()


