import unittest
import ast
from detection_rules.generic.broadcasting_feature_not_used import (
    BroadcastingFeatureNotUsedSmell,
)


class TestBroadcastingFeatureNotUsedSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the
        BroadcastingFeatureNotUsedSmell instance.
        """
        self.smell_detector = BroadcastingFeatureNotUsedSmell()

    def test_detect_no_smell(self):
        """
        Test the detect method when no misuse of broadcasting is present.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    tensor_a = tf.constant([[1], [2], [3]])\n"
            "    tensor_b = tf.constant([1, 2, 3])\n"
            "    tensor_c = tensor_a + tensor_b\n"
            # Broadcasting applied correctly
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell(self):
        """
        Test the detect method when tiling is unnecessarily
        used instead of broadcasting.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    tensor_a = tf.constant([[1], [2], [3]])\n"
            "    tensor_b = tf.constant([1, 2, 3])\n"
            "    tensor_a_tiled = tf.tile(tensor_a, [1, 3])\n"
            "    tensor_c = tensor_a_tiled + tensor_b\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "Broadcasting_Feature_Not_Used")
        self.assertIn("unnecessary tiling", result[0]["additional_info"])
        self.assertEqual(result[0]["line"], 6)  # Line where the smell occurs

    def test_detect_without_tensorflow_library(self):
        """
        Test the detect method when the TensorFlow library is not imported.
        """
        code = (
            "def main():\n"
            "    tensor_a = [[1], [2], [3]]\n"
            "    tensor_b = [1, 2, 3]\n"
            "    tensor_c = [row + tensor_b for row in tensor_a]\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No TensorFlow alias
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_multiple_smells(self):
        """
        Test the detect method when multiple tiling misuses are present.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    tensor_a = tf.constant([[1], [2], [3]])\n"
            "    tensor_b = tf.constant([1, 2, 3])\n"
            "    tensor_a_tiled = tf.tile(tensor_a, [1, 3])\n"
            "    tensor_c = tensor_a_tiled + tensor_b\n"
            "    tensor_d = tf.tile(tensor_b, [3, 1]) + tensor_a\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 2)  # Two smells should be detected
        self.assertEqual(result[0]["line"], 6)  # Line of the first smell
        self.assertEqual(result[1]["line"], 7)  # Line of the second smell


if __name__ == "__main__":
    unittest.main()
