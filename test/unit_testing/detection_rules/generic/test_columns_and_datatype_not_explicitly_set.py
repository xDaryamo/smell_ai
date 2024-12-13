import unittest
import ast
from detection_rules.generic.columns_and_datatype_not_explicitly_set import (
    ColumnsAndDatatypeNotExplicitlySetSmell,
)


class TestColumnsAndDatatypeNotExplicitlySetSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the
        ColumnsAndDatatypeNotExplicitlySetSmell instance.
        """
        self.smell_detector = ColumnsAndDatatypeNotExplicitlySetSmell()

    def test_detect_no_smell(self):
        """
        Test the detect method when no misuse of
        dtype specification is present.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    data = {'column1': [1, 2], 'column2': [3, 4]}\n"
            "    df = pd.DataFrame(data, dtype='float')\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell_dataframe(self):
        """
        Test the detect method when dtype is not explicitly set in DataFrame.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    data = {'column1': [1, 2], 'column2': [3, 4]}\n"
            "    df = pd.DataFrame(data)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(
            result[0]["name"], "columns_and_datatype_not_explicitly_set"
        )
        self.assertIn("Missing explicit 'dtype'", result[0]["additional_info"])
        self.assertEqual(result[0]["line"], 4)  # Line where the smell occurs

    def test_detect_with_smell_read_csv(self):
        """
        Test the detect method when dtype is not explicitly set in read_csv.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.read_csv('file.csv')\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(
            result[0]["name"], "columns_and_datatype_not_explicitly_set"
        )
        self.assertIn("Missing explicit 'dtype'", result[0]["additional_info"])
        self.assertEqual(result[0]["line"], 3)  # Line where the smell occurs

    def test_detect_without_pandas_library(self):
        """
        Test the detect method when the Pandas library is not imported.
        """
        code = (
            "def main():\n"
            "    data = {'column1': [1, 2], 'column2': [3, 4]}\n"
            "    df = DataFrame(data)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No Pandas alias
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_multiple_smells(self):
        """
        Test the detect method when multiple instances
        of missing dtype are present.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    data = {'column1': [1, 2], 'column2': [3, 4]}\n"
            "    df1 = pd.DataFrame(data)\n"
            "    df2 = pd.read_csv('file.csv')\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "variables": {},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 2)  # Two smells should be detected
        self.assertEqual(result[0]["line"], 4)  # Line of the first smell
        self.assertEqual(result[1]["line"], 5)  # Line of the second smell


if __name__ == "__main__":
    unittest.main()
