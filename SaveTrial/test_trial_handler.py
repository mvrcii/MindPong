import unittest

import numpy as np
import MetaData
import Labels

import trial_handler


class MyTestCase(unittest.TestCase):
    def test_save_trial(self):
        array = [[x for x in range(3)] for i in range(16)]
        array2 = [[x for x in range(5, 7)] for i in range(16)]
        trial_handler.save_trial(array, Labels.Labels.LEFT)
        trial_handler.save_trial(array2, Labels.Labels.LEFT)
        expected_array = [[0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6]]

        print(trial_handler.trial_buffer)
        self.assertEqual(expected_array, trial_handler.trial_buffer)

    def test_save_session(self):
        array = [[x for x in range(3)] for i in range(16)]
        array2 = [[x for x in range(5, 7)] for i in range(16)]
        trial_handler.save_trial(array, Labels.Labels.LEFT)
        trial_handler.save_trial(array2, Labels.Labels.LEFT)
        expected_array = [[0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6]]
        expected_array = np.array(expected_array)
        ses = MetaData.MetaData(sid=1, amount_samples=3, amount_trials=2)
        metadata = ses.turn_into_np_array()
        expected_metadata = metadata
        expected_pos = np.array([0,3])
        trial_handler.save_session(metadata, 'test.npz')
        test = np.load('../Session/test.npz', allow_pickle=True)
        self.assertEqual(test['meta'].all(), expected_metadata.all())
        self.assertEqual(test['raw_data'].all(), expected_array.all())
        self.assertEqual(test['position'].all(), expected_pos.all())



if __name__ == '__main__':
    unittest.main()
