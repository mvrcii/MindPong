import unittest
import cursor_online_control as coc


class TestCursorOnlineMethods(unittest.TestCase):
    """
    A Class to test the Curser Online Methods

    """

    def setUp(self):
        """
        To set up
        """
        self.expected = [1,2,3,4,5,6,7,8,9]
        self.expected_list = [[0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0]]
        self.exampleData = [[1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9]]
        self.examleList = [[1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]]

    def test_calculate_small_laplacian(self):
        """
        To test calculate small laplacian
        """
        result = coc.calculate_small_laplacian(self.exampleData[0], self.exampleData[1],self.exampleData[2], self.exampleData[3])
        self.assertListEqual(result, self.expected)

    def test_calculate_spatial_filtering(self):
        """
        To test calculate small laplacian
        """
        print("Test2")
        result = coc.calculate_spatial_filtering(self.examleList)
        print(result)
        self.assertListEqual(result, self.expected_list)


if __name__ == "__main__":
    unittest.main()
