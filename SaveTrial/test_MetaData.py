import datetime
import unittest
import MetaData
import numpy as np


class MyTestCase(unittest.TestCase):
    def test_turn_into_np_array(self):
        time = datetime.datetime.now().time()
        session = MetaData.MetaData(sid=1, amount_samples=25, amount_trials=7, time=time)
        meta = [('id', 1), ('date', datetime.date.today()), ('time', time), ('amount_samples', 25),
                ('sampling_rate', 125), ('channels', session.channel_mapping), ('amount_trials', 7)]
        self.assertEqual(np.array(meta, dtype=object).all(), session.turn_into_np_array().all())  # add assertion here


if __name__ == '__main__':
    unittest.main()
