import time
import unittest
import read_pylsl_stream as rps


class TestReadStream(unittest.TestCase):

    def test_create_sliding_window(self):
        rps.window_size = 125
        rps.data = [[0] * 16 for _ in range(rps.window_size)]
        rps.offset = 12
        rps.offset_data = [[0] * 16 for _ in range(rps.offset)]
        for i in range(16):
            rps.data[rps.offset][i] = -1
        test_array = rps.data[rps.offset]
        for i in range(16):
            for j in range(rps.offset):
                rps.offset_data[j][i] = i + j
        rps.create_sliding_window()

        self.assertEqual(rps.window_size, len(rps.data))
        self.assertEqual(rps.offset_data[rps.offset-1], rps.data[rps.window_size-1])
        self.assertEqual(rps.offset_data[0], rps.data[rps.window_size - rps.offset])
        self.assertEqual(test_array, rps.data[0])


if __name__ == '__main__':
    unittest.main()
