import unittest
import ast
from detection_rules.api_specific.tensor_array_not_used import (
    TensorArrayNotUsedSmell,
)


class TestTensorArrayNotUsedSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the TensorArrayNotUsedSmell instance.
        """
        self.smell_detector = TensorArrayNotUsedSmell()

    def test_detect_no_smell(self):
        """
        Test the detect method when no misuse of `tf.constant()` is present.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    x = tf.constant([1, 2, 3])\n"
            "    y = tf.constant([4, 5, 6])\n"
            "    result = tf.concat([x, y], axis=0)\n"
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
        Test the detect method when `tf.constant()` is modified inside a loop.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    x = tf.constant([1, 2, 3])\n"
            "    for i in range(3):\n"
            "        x = tf.concat([x, tf.constant([i])], axis=0)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "tensor_array_not_used")
        self.assertIn(
            "Using `tf.TensorArray` is better", result[0]["additional_info"]
        )
        self.assertEqual(result[0]["line"], 5)  # Line where the smell occurs

    def test_detect_without_tensorflow_library(self):
        """
        Test the detect method when the TensorFlow library is not imported.
        """
        code = (
            "def main():\n"
            "    x = [1, 2, 3]\n"
            "    for i in range(3):\n"
            "        x.append(i)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No TensorFlow alias
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_nested_concat(self):
        """
        Test the detect method with nested `tf.concat` inside a loop.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    x = tf.constant([1, 2, 3])\n"
            "    for i in range(3):\n"
            "        x = tf.concat("
            "    [x, tf.concat([tf.constant([i])], axis=0)], axis=0"
            ")\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "tensor_array_not_used")
        self.assertIn(
            "Using `tf.TensorArray` is better", result[0]["additional_info"]
        )
        self.assertEqual(result[0]["line"], 5)  # Line where the smell occurs

    def test_detect_constant_not_in_loop(self):
        """
        Test the detect method when `tf.constant()` is used but not in a loop.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    x = tf.constant([1, 2, 3])\n"
            "    x = tf.concat([x, tf.constant([4])], axis=0)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_tensor_modified_outside_loop(self):
        """
        Test the detect method when `tf.constant()` is modified outside a loop.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    x = tf.constant([1, 2, 3])\n"
            "    x = tf.concat([x, tf.constant([4])], axis=0)\n"
            "    for i in range(3):\n"
            "        y = tf.constant([i])\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected


if __name__ == "__main__":
    unittest.main()
