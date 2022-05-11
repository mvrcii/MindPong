import datetime
import unittest
import numpy as np

from scripts.mvc.models import MetaData


class TestMetaDataClass(unittest.TestCase):
    def test_convert_to_np_array(self):
        # GIVEN
        time = datetime.datetime.now().time()
        meta = [['id', 1], ['sex', 'f'], ['age', 27], ['date', datetime.date.today()], ['time', time],
                ['sampling_rate', 125], ['channels', MetaData.bci_channels],
                ['recording_type', 'game'], ['headset', 'BCI'], ['amount_trials', 7], ['different_events', 2],
                ['comment', 'hallo']]

        # WHEN
        session = MetaData(sid=1, sex='f', age=27, amount_events=2, comment='hallo', amount_trials=7,
                                      time=time)

        # THEN
        self.assertEqual(meta, session.turn_into_np_array().tolist())


if __name__ == '__main__':
    unittest.main()
