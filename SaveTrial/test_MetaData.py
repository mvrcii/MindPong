import datetime
import unittest
import MetaData
import numpy as np


class MyTestCase(unittest.TestCase):
    def test_turn_into_np_array(self):
        time = datetime.datetime.now().time()
        session = MetaData.MetaData(sid=1, sex='f', age=27, amount_events=2, comment='hallo', amount_trials=7,
                                    time=time)
        meta = [('id', 1), ('sex', 'f'), ('age', 27), ('date', datetime.date.today()), ('time', time),
                ('sampling_rate', 125), ('channels', MetaData.MetaData.bci_channels),
                ('recording_type', 'game'), ('headset', 'BCI'), ('amount_trials', 7), ('different_events', 2),
                ('comment', 'hallo')]
        self.assertEqual(np.array(meta, dtype=object).all(), session.turn_into_np_array().all())


if __name__ == '__main__':
    unittest.main()
