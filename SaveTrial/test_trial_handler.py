import datetime
import unittest

import numpy as np
import MetaData
import Labels

import trial_handler


class MyTestCase(unittest.TestCase):
    def test_save_trial(self):
        junk = [[9 for x in range(3)] for i in range(16)]
        trial = [[x for x in range(3)] for i in range(16)]
        junk2 = [[8 for x in range(3)] for i in range(16)]
        trial2 = [[x for x in range(5, 7)] for i in range(16)]
        trial_handler.save_trial(trial, junk, Labels.Labels.LEFT)
        trial_handler.save_trial(trial2, junk2, Labels.Labels.LEFT)
        expected_array = [[] for _ in range(16)]
        for i in range(len(expected_array)):
            expected_array[i] = [9, 9, 9, 0, 1, 2, 8, 8, 8, 5, 6]
        print(trial_handler.raw_data)
        self.assertEqual(expected_array, trial_handler.raw_data)

    def test_save_session(self):
        junk = [[9 for x in range(3)] for i in range(16)]
        trial = [[x for x in range(3)] for i in range(16)]
        junk2 = [[8 for x in range(3)] for i in range(16)]
        trial2 = [[x for x in range(5, 7)] for i in range(16)]
        trial_handler.save_trial(trial, junk, Labels.Labels.LEFT)
        trial_handler.save_trial(trial2, junk2, Labels.Labels.LEFT)
        expected_array = [[] for _ in range(16)]
        for i in range(len(expected_array)):
            expected_array[i] = [9, 9, 9, 0, 1, 2, 8, 8, 8, 5, 6]
        expected_array = np.array(expected_array)
        time = datetime.datetime.now().time()
        ses = MetaData.MetaData(sid=1, sex='f', age=27, amount_events=2, comment='hallo', amount_trials=7,
                                time=time)
        meta = [('id', 1), ('sex', 'f'), ('age', 27), ('date', datetime.date.today()), ('time', time),
                ('sampling_rate', 125), ('channels', MetaData.MetaData.bci_channels),
                ('recording_type', 'game'), ('headset', 'BCI'), ('amount_trials', 7), ('different_events', 2),
                ('comment', 'hallo')]
        metadata = ses.turn_into_np_array()
        expected_metadata = np.array(meta, dtype=object)
        expected_pos = np.array([3, 9])
        expected_duration = np.array([3, 2])
        expected_type = np.array([Labels.Labels.LEFT, Labels.Labels.LEFT])
        trial_handler.save_session(metadata, 'test.npz')
        test = np.load('../Session/test.npz', allow_pickle=True)
        self.assertEqual(test['meta'].all(), expected_metadata.all())
        self.assertEqual(test['raw_data'].all(), expected_array.all())
        self.assertEqual(test['event_pos'].all(), expected_pos.all())
        self.assertEqual(test['event_type'].all(), expected_type.all())
        self.assertEqual(test['event_duration'].all(), expected_duration.all())


if __name__ == '__main__':
    unittest.main()
