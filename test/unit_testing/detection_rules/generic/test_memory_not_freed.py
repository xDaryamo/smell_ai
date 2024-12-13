import unittest
import ast
from detection_rules.generic.memory_not_freed import MemoryNotFreedSmell


class TestMemoryNotFreedSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the MemoryNotFreedSmell instance.
        """
        self.smell_detector = MemoryNotFreedSmell()

    def test_detect_no_smell(self):
        """
        Test the detect method when no memory is mismanaged.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    model = tf.keras.Sequential()\n"
            "    tf.keras.backend.clear_session()\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell(self):
        """
        Test the detect method when memory is not freed inside a loop.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    for i in range(10):\n"
            "        model = tf.keras.Sequential()\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "memory_not_freed")
        self.assertIn(
            "Memory not freed after model definition",
            result[0]["additional_info"],
        )
        self.assertEqual(result[0]["line"], 3)  # Line where the smell occurs

    def test_detect_with_memory_freed(self):
        """
        Test the detect method when memory is freed inside a loop.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    for i in range(10):\n"
            "        model = tf.keras.Sequential()\n"
            "        tf.keras.backend.clear_session()\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_without_tensorflow_library(self):
        """
        Test the detect method when TensorFlow library is not imported.
        """
        code = (
            "def main():\n"
            "    for i in range(10):\n"
            "        model = Sequential()\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # TensorFlow not imported
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_multiple_loops_with_and_without_smells(self):
        """
        Test the detect method when multiple loops are present,
        some with and some without memory mismanagement.
        """
        code = (
            "import tensorflow as tf\n"
            "def main():\n"
            "    for i in range(5):\n"
            "        model = tf.keras.Sequential()\n"
            "    for j in range(5):\n"
            "        model = tf.keras.Sequential()\n"
            "        tf.keras.backend.clear_session()\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"tensorflow": "tf"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["line"], 3)  # Line of the smell


if __name__ == "__main__":
    unittest.main()
