import unittest

import numpy as np
from tests.data.analysis import BCIC_dataset_loader as bdl
from scripts.data.analysis import cursor_control_algorithm

# constants
TMIN = 100.0  # Minimum time value shown in the following figures
TMAX = 850.0  # Maximum time value shown in the following figures


class ConfigData:
    def __init__(self):
        self.threshold = 1.5
        self.f_min = 8
        self.f_max = 12
        self.window_size = 1.0
        self.window_offset = 0.05
        self.offset_in_percentage = self.window_size / self.window_offset / 100.0
        self.sampling_rate = 250
        self.draw_plot = True


def load_bcic_dataset(ch_weight):
    """
    - converts ch_weight into the corresponding channels and inserts C3 and C4 to the first two places in the list
    - provides the BCIC dataset for further processing
    :param ch_weight: weighted array to set channel selection
    :return: loaded_data: contains the samples of all channels
                Structure of 2-dim array from the data loader:
                        dim 0: EEG channel
                        dim 1: sample
             loaded_labels: contains the corresponding label for each trial
    """
    # Load BCIC dataset
    used_ch_names = []
    # map ch_weight(channel selection) with channels names in BCI dataset to load to selected channels
    for i in range(len(bdl.CHANNELS)):
        if ch_weight[i] != 0:
            if bdl.CHANNELS[i] == 'C3':
                used_ch_names.insert(0, bdl.CHANNELS[i])
            elif bdl.CHANNELS[i] == 'C4':
                used_ch_names.insert(1, bdl.CHANNELS[i])
            else:
                used_ch_names.append(bdl.CHANNELS[i])

    chan_data, label_data = bdl.get_channel_rawdata(subject=7, n_class=2, ch_names=used_ch_names)

    return chan_data, label_data, used_ch_names


def test_algorithm(chan_data, label_data, used_ch_names):
    """
    - create overlapping sliding windows
    - Calls the cursor control algorithm
    - calculate und plot accuracy
    :return: None
    """
    config = ConfigData()
    accuracy = 0
    found_label = False
    num_valid_sliding_windows = 0
    n_slices = int((TMAX - TMIN - config.window_size) / config.offset_in_percentage)
    toff = np.zeros(n_slices, dtype=float)
    label = np.zeros(n_slices, dtype=int)
    for i in range(n_slices):
        toff[i] = TMIN + i * config.offset_in_percentage
        label[i] = label_data[int((TMIN + i * config.offset_in_percentage) * config.sampling_rate)]
        start_idx = int(toff[i] * config.sampling_rate)
        stop_idx = int(((toff[i] + config.window_size) * config.sampling_rate) - 1)

        # calls the one and only cursor control algorithm
        calculated_label = cursor_control_algorithm.perform_algorithm(chan_data[:, start_idx:stop_idx], used_ch_names, config.sampling_rate, data_mdl=config, offset_in_percentage=config.offset_in_percentage)

        # compare the calculated label with the predefined label, if same -> increase accuracy
        if label[i] != -1:
            if label[i] == calculated_label:
                found_label = True

        if label[i] != label[i-1]:
            if found_label:
                accuracy += 1

            found_label = False
            num_valid_sliding_windows += 0.5

    # calculate und plot accuracy
    num_valid_sliding_windows = int(num_valid_sliding_windows)
    print(f'accuracy: {accuracy}\nnum_sliding_windows: {num_valid_sliding_windows}')
    accuracy /= num_valid_sliding_windows
    print(f'Accuracy = {accuracy}')


def sort_incoming_channels(sliding_window, used_ch_names):
    #                 'C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1', 'O2', 'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2', 'CP6'
    ch_names_weight = [1,    0,    1,    0,    0,    0,    0,    0,     1,     1,     1,     1,     1,     1,     1,    1]

    #                 'C3', 'Cz', 'C4', 'P3', '?', 'P4', 'T3', '?', '?', 'F3', 'F4', '?', '?', '?', '?', 'T4'
    ch_names_weight = [1,    1,    1,    1,    0,    1,    1,   0,   0,   1,    1,    0,   0,   0,   0,    1]

    filtered_sliding_window = list()
    filtered_channel_names = list()
    for i in range(len(used_ch_names)):
        if ch_names_weight[i] != 0:
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


def test_algorithm_with_dataset():
    #                 Fz  FC3  FC1  FCz  FC2  FC4  C5  C3  C1  Cz  C2  C4  C6  CP3  CP1  CPz  CP2  CP4  P1  Pz  P2  POz
    ch_names_weight = [0,  1,   1,   0,   1,   1,   0,  1,  0,  0,  0,  1,  0,  1,   1,   0,   1,   1,   0,  0,  0,  0]
    preloaded_data, preloaded_labels, used_ch_names = load_bcic_dataset(ch_names_weight)
    test_algorithm(preloaded_data, preloaded_labels, used_ch_names)


class TestCursorControlAlgorithm(unittest.TestCase):
    # See: https://stackoverflow.com/questions/14305941/run-setup-only-once-for-a-set-of-automated-tests
    @classmethod
    def setUpClass(cls):
        """
        Sets up unit test:
            - loads BCIC data
        """
        cls.preloaded_data = load_bcic_dataset([0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0])[0]

    def setUp(self) -> None:
        """
        Sets up for each unit test:
            - gets BCIC data
        """
        self.preloaded_data = TestCursorControlAlgorithm.preloaded_data

    def test_bcic_loader(self) -> None:
        """
        Tests BCIC loader
        """
        self.expected = [0.00000, -5.19902, -4.98199, -1.59162, -4.06636, 1.64937, 1.06276, 6.46272, 4.92175, 4.05145,
                         7.59516, 6.20126, 6.09107, 7.72394, 6.74819, 7.14356, 4.94263, 8.94099, 13.21054, 14.13214,
                         14.65140, 7.83529, 6.76266, 0.58230, -7.19526, -7.52891, -11.83081, -7.76881, -11.94738, -12.35955,
                         -10.61692, -9.71974, -3.45298, -2.50503, -0.23939, 0.21074, 0.05776, 2.13291, -0.87473, -5.01351,
                         -2.14486, -8.18198, -1.90035, -2.85811, -5.88188, -1.71824, -4.94796, -2.46665, -5.91495, -7.72628,
                         -5.09891, -4.64259, -2.93458, -8.53198, -9.03389, -11.02019, -12.98102, -3.84274, -6.85336, -2.48155,
                         -0.53602, -4.76626, -0.79484, -1.56047, -1.54331, 1.35544, 0.27490, 3.71789, 5.58870, 7.79345,
                         6.51788, 5.26750, 5.39956, 3.36294, 4.48316, 7.18784, 6.15883, 11.81859, 8.51150, 6.59374,
                         9.02904, 3.53276, 13.25546, 6.04107, 5.52800, 8.42714, 2.27360, 3.95059, 0.88638, 0.21508,
                         -0.18306, -1.52482, 1.67802, 2.71492, -1.63083, 0.87526, -6.34793, -5.81899, -8.05545, -8.31231]
        self.result = self.preloaded_data[0][0:100]
        np.testing.assert_array_almost_equal(self.result, self.expected, decimal=5)

    def test_standardize_data_method(self) -> None:
        """
        Tests standardize_data() method
        """
        self.data = self.preloaded_data[0][0:100]
        from scripts.data.analysis.cursor_control_algorithm import standardize_data
        self.result = standardize_data(self.data)
        std = np.std(self.result)
        np.testing.assert_almost_equal(np.mean(self.result), 0, decimal=5)
        np.testing.assert_almost_equal(np.std(self.result), 1, decimal=5)

    def test_calculate_laplacian_method(self) -> None:
        pass

    def test_split_laplacian_areas_method(self) -> None:
        pass

    def test_integrate_psd_values_method(self) -> None:
        pass

    def test_manage_ringbuffer_method(self) -> None:
        pass
