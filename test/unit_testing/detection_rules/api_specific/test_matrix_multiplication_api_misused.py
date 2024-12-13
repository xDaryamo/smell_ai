import unittest
import ast
from detection_rules.api_specific.matrix_multiplication_api_misused import (
    MatrixMultiplicationAPIMisused,
)


class TestMatrixMultiplicationAPIMisused(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the MatrixMultiplicationAPIMisused instance.
        """
        self.smell_detector = MatrixMultiplicationAPIMisused()

    def test_detect_no_smell(self):
        """
        Test the detect method when no misuse of `dot()` is present.
        """
        code = (
            "import numpy as np\n"
            "matrix1 = [[1, 2], [3, 4]]\n"
            "matrix2 = [[5, 6], [7, 8]]\n"
            "result = np.matmul(matrix1, matrix2)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"numpy": "np"},
            "lines": {i + 1: line for i, line in enumerate(code.splitlines())},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell(self):
        """
        Test the detect method when `dot()`
        is misused for matrix multiplication.
        """
        code = (
            "import numpy as np\n"
            "matrix1 = [[1, 2], [3, 4]]\n"
            "matrix2 = [[5, 6], [7, 8]]\n"
            "result = np.dot(matrix1, matrix2)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"numpy": "np"},
            "lines": {i + 1: line for i, line in enumerate(code.splitlines())},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(
            result[0]["name"], "matrix_multiplication_api_misused"
        )
        self.assertIn(
            "Detected misuse of `dot()`", result[0]["additional_info"]
        )
        self.assertEqual(result[0]["line"], 4)  # Line where the smell occurs

    def test_detect_without_numpy_library(self):
        """
        Test the detect method when the NumPy library is not imported.
        """
        code = (
            "matrix1 = [[1, 2], [3, 4]]\n"
            "matrix2 = [[5, 6], [7, 8]]\n"
            "result = dot(matrix1, matrix2)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No NumPy alias
            "lines": {i + 1: line for i, line in enumerate(code.splitlines())},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_multiple_smells(self):
        """
        Test the detect method when multiple `dot()` misuses are present.
        """
        code = (
            "import numpy as np\n"
            "matrix1 = [[1, 2], [3, 4]]\n"
            "matrix2 = [[5, 6], [7, 8]]\n"
            "result1 = np.dot(matrix1, matrix2)\n"
            "result2 = np.dot(matrix2, matrix1)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"numpy": "np"},
            "lines": {i + 1: line for i, line in enumerate(code.splitlines())},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 2)  # Two smells should be detected
        self.assertEqual(result[0]["line"], 4)  # Line of the first smell
        self.assertEqual(result[1]["line"], 5)  # Line of the second smell


if __name__ == "__main__":
    unittest.main()
