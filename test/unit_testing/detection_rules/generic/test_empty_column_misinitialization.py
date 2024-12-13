import unittest
import ast
from detection_rules.generic.empty_column_misinitialization import (
    EmptyColumnMisinitializationSmell,
)


class TestEmptyColumnMisinitializationSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the
        EmptyColumnMisinitializationSmell instance.
        """
        self.smell_detector = EmptyColumnMisinitializationSmell()

    def test_detect_no_smell(self):
        """
        Test the detect method when no column misinitialization is present.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df['new_column'] = pd.NA\n"  # Proper initialization
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_zero_initialization(self):
        """
        Test the detect method when a column is initialized with zero.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df['new_column'] = 0\n"  # Misinitialization
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "empty_column_misinitialization")
        self.assertIn("initialized with a zero", result[0]["additional_info"])
        self.assertEqual(result[0]["line"], 4)  # Line where the smell occurs

    def test_detect_with_empty_string_initialization(self):
        """
        Test the detect method when a
        column is initialized with an empty string.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df['new_column'] = ''\n"  # Misinitialization
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "empty_column_misinitialization")
        self.assertIn(
            "initialized with a zero or empty string",
            result[0]["additional_info"],
        )
        self.assertEqual(result[0]["line"], 4)  # Line where the smell occurs

    def test_detect_without_pandas_library(self):
        """
        Test the detect method when the Pandas library is not imported.
        """
        code = (
            "def main():\n"
            "    df = {'a': [1, 2, 3]}\n"
            "    df['new_column'] = 0\n"  # This should not be flagged
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No Pandas alias
            "dataframe_variables": [],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_multiple_smells(self):
        """
        Test the detect method when multiple
        column misinitializations are present.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df['col1'] = 0\n"
            "    df['col2'] = ''\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 2)  # Two smells should be detected
        self.assertEqual(result[0]["line"], 4)  # Line of the first smell
        self.assertEqual(result[1]["line"], 5)  # Line of the second smell


if __name__ == "__main__":
    unittest.main()
