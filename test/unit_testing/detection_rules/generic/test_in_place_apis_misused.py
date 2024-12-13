import unittest
import ast
from detection_rules.generic.in_place_apis_misused import (
    InPlaceAPIsMisusedSmell,
)


class TestInPlaceAPIsMisusedSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the InPlaceAPIsMisusedSmell instance.
        """
        self.smell_detector = InPlaceAPIsMisusedSmell()

    def test_detect_no_smell_with_inplace_true(self):
        """
        Test the detect method when `inplace=True` is explicitly set.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df.drop(columns=['a'], inplace=True)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
            "dataframe_methods": ["drop"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_inplace_false(self):
        """
        Test the detect method when `inplace=False` is explicitly set.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df.drop(columns=['a'], inplace=False)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
            "dataframe_methods": ["drop"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "in_place_apis_misused")
        self.assertIn(
            "Explicitly setting `inplace=False`", result[0]["additional_info"]
        )
        self.assertEqual(result[0]["line"], 4)  # Line where the smell occurs

    def test_detect_no_smell_with_assignment(self):
        """
        Test the detect method when the result
        of a method call is assigned to a variable.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    new_df = df.drop(columns=['a'])\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
            "dataframe_methods": ["drop"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_no_inplace_and_no_assignment(self):
        """
        Test the detect method when neither `inplace`
        is set nor the result is assigned.
        """
        code = (
            "import pandas as pd\n"
            "def main():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    df.drop(columns=['a'])\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
            "dataframe_methods": ["drop"],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "in_place_apis_misused")
        self.assertIn(
            "not assigned to a variable, and the `inplace` "
            "parameter is not explicitly set",
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
            "    df.drop(columns=['a'], inplace=False)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No Pandas alias
            "dataframe_variables": [],
            "dataframe_methods": [],
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected


if __name__ == "__main__":
    unittest.main()
