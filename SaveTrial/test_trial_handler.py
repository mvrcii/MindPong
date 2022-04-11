import datetime
import time
import unittest

import numpy as np
from numpy import dtype

import MetaData
import Labels

import trial_handler


class MyTestCase(unittest.TestCase):

    def setUp(self):
        trial_handler.raw_data = [[] for _ in range(16)]
        trial_handler.event_pos = []
        trial_handler.event_duration = []
        trial_handler.event_type = []

    def test_send_raw_data(self):
        data1 = [[1] for _ in range(16)]
        data2 = [[2] for _ in range(16)]
        data3 = [[3] for _ in range(16)]
        data4 = [[4] for _ in range(16)]
        trial_handler.send_raw_data(data1, start=time.time())
        trial_handler.send_raw_data(data2)
        trial_handler.send_raw_data(data3)
        trial_handler.send_raw_data(data4)
        expected_array = [[] for _ in range(16)]
        for i in range(len(expected_array)):
            expected_array[i] = [1, 2, 3, 4]
        self.assertEqual(expected_array, trial_handler.raw_data)

    def test_mark_trial(self):
        data1 = [[1] for _ in range(16)]
        start = time.time()
        trial_handler.send_raw_data(data1, start=start)
        trial_handler.mark_trial(start + 0.008, start + (0.008 * 5), Labels.Labels.LEFT)
        self.assertEqual(1, trial_handler.event_pos[0])
        self.assertEqual(4, trial_handler.event_duration[0])
        self.assertEqual(Labels.Labels.LEFT, trial_handler.event_type[0])

    def test_save_session(self):
        data1 = [[1] for _ in range(16)]
        data2 = [[2] for _ in range(16)]
        data3 = [[3] for _ in range(16)]
        data4 = [[4] for _ in range(16)]
        start = time.time()
        trial_handler.send_raw_data(data1, start=start)
        trial_handler.send_raw_data(data2)
        trial_handler.send_raw_data(data3)
        trial_handler.send_raw_data(data4)
        trial_handler.mark_trial(start + 0.008, start + (0.008 * 5), Labels.Labels.LEFT)
        expected_array = [[] for _ in range(16)]
        for i in range(len(expected_array)):
            expected_array[i] = [1, 2, 3, 4]
        expected_array = np.array(expected_array)

        timestamp = datetime.datetime.now().time()
        ses = MetaData.MetaData(sid=1, sex='f', age=27, amount_events=2, comment='hallo', amount_trials=7,
                                time=timestamp)
        meta = [('id', 1), ('sex', 'f'), ('age', 27), ('date', datetime.date.today()), ('time', time),
                ('sampling_rate', 125), ('channels', MetaData.MetaData.bci_channels),
                ('recording_type', 'game'), ('headset', 'BCI'), ('amount_trials', 7), ('different_events', 2),
                ('comment', 'hallo')]
        metadata = ses.turn_into_np_array()
        expected_metadata = np.array(meta, dtype=dtype)
        expected_pos = np.array([1])
        expected_duration = np.array([4])
        expected_type = np.array([Labels.Labels.LEFT])
        trial_handler.save_session(metadata, 'test.npz')
        test = np.load('../Session/test.npz', allow_pickle=True)
        self.assertEqual(test['meta'].all(), expected_metadata.all())
        self.assertEqual(test['raw_data'].all(), expected_array.all())
        self.assertEqual(test['event_pos'].all(), expected_pos.all())
        self.assertEqual(test['event_type'].all(), expected_type.all())
        self.assertEqual(test['event_duration'].all(), expected_duration.all())



if __name__ == '__main__':
    unittest.main()
