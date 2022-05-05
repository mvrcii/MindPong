import unittest
import numpy as np

from scripts.data.loader import game_dataset_loader


class MyTestCase(unittest.TestCase):

    def test_get_channel_rawdata(self):

        game_dataset_loader.NOTCH_FILTER = True
        game_dataset_loader.NOTCH_FILTER_FREQ = 50.0

        chan_data, chan_label = game_dataset_loader.get_channel_rawdata('../../../scripts/data/session/test_loader.npz')
        expected_chan_data = np.array([[1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898]])
        expected_chan_label = np.array([-1, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])

        for a, b in zip(expected_chan_data, chan_data):
            for c, d in zip(a, b):
                self.assertAlmostEqual(q, d, 2)
        for a, b in zip(expected_chan_label, chan_label):
            self.assertAlmostEqual(a, b, 2)

        chan_data, chan_label = game_dataset_loader.get_channel_rawdata('../../../scripts/data/session/test_loader.npz',
                                                                        ['C4', 'C3'])
        expected_chan_data = np.array([[1.0369846, 1.9401181, 3.05990587, 3.96296898],
                                       [1.0369846, 1.9401181, 3.05990587, 3.96296898]])

        for a, b in zip(expected_chan_data, chan_data):
            for c, d in zip(a, b):
                self.assertAlmostEqual(c, d, 2)
        for a, b in zip(expected_chan_label, chan_label):
            self.assertAlmostEqual(a, b, 2)

        chan_data, chan_label = game_dataset_loader.get_channel_rawdata('../../../scripts/data/session/test_loader.npz',
                                                                        ['C4', 'C3', 'not a channel name'])
        self.assertEqual(None, chan_data)
        self.assertEqual(None, chan_label)


if __name__ == '__main__':
    unittest.main()
