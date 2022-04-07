import unittest
import trial_handler


class MyTestCase(unittest.TestCase):
    def test_save_trial(self):
        array = [[x for x in range(3)] for i in range(16)]
        array2 = [[x for x in range(5, 7)] for i in range(16)]
        trial_handler.save_trial(array)
        trial_handler.save_trial(array2)
        expected_array = [[0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6], [0, 1, 2, 5, 6],
                          [0, 1, 2, 5, 6]]

        print(trial_handler.buffer)
        self.assertEqual(expected_array, trial_handler.buffer)


if __name__ == '__main__':
    unittest.main()
