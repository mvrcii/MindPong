import datetime
import unittest
import numpy as np

import scripts.data.extraction as extraction


class TestMetaDataClass(unittest.TestCase):
    def test_convert_to_np_array(self):
        # GIVEN
        time = datetime.datetime.now().time()
        meta = [('id', 1), ('sex', 'f'), ('age', 27), ('date', datetime.date.today()), ('time', time),
                ('sampling_rate', 125), ('channels', extraction.MetaData.bci_channels),
                ('recording_type', 'game'), ('headset', 'BCI'), ('amount_trials', 7), ('different_events', 2),
                ('comment', 'hallo')]

        # WHEN
        session = extraction.MetaData(sid=1, sex='f', age=27, amount_events=2, comment='hallo', amount_trials=7,
                                      time=time)

        # THEN
        self.assertEqual(np.array(meta, dtype=object).all(), session.turn_into_np_array().all())


if __name__ == '__main__':
    unittest.main()
