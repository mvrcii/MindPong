import unittest
import read_pylsl_stream
import pylsl


class TestReadStream(unittest.TestCase):
    def stream(self):
        info = pylsl.StreamInfo('name', 'EEG', 16, 125, 12345)
        outlet = pylsl.StreamOutlet(info)
        #outlet.push_chunk()
        return pylsl.resolve_byprop('name', 'EEG', timeout=10)

    def test_empty_stream_init(self):
        self.assertEqual(read_pylsl_stream.init([]), False)  # add assertion here

    def test_full_stream_init(self):
        self.assertEqual(read_pylsl_stream.init(self.stream()), True)


if __name__ == '__main__':
    unittest.main()
