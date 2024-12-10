import unittest
import ast
from detection_rules.api_specific.chain_indexing_smell import ChainIndexingSmell


class TestChainIndexingSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the ChainIndexingSmell instance and common data.
        """
        self.smell_detector = ChainIndexingSmell()
        self.filename = "test_file.py"

    def test_detect_no_smell(self):
        """
        Test the detect method when no chained indexing is present.
        """
        # Code with no chained indexing
        code = (
            "import pandas as pd\n"
            "df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "value = df.loc[0, 'a']\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data, self.filename)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell(self):
        """
        Test the detect method when chained indexing is present.
        """
        # Code with chained indexing
        code = (
            "import pandas as pd\n"
            "df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "value = df['a'][0]\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data, self.filename)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(result[0]["name"], "Chain_Indexing")
        self.assertIn("Chained indexing detected", result[0]["additional_info"])
        self.assertEqual(result[0]["line"], 3)  # Line where the smell occurs

    def test_detect_without_pandas_library(self):
        """
        Test the detect method when the pandas library is not imported.
        """
        code = "df = {'a': [1, 2, 3]}\n" "value = df['a'][0]\n"
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No pandas alias
            "dataframe_variables": [],
        }

        result = self.smell_detector.detect(tree, extracted_data, self.filename)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_multiple_smells(self):
        """
        Test the detect method when multiple chained indexings are present.
        """
        code = (
            "import pandas as pd\n"
            "df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "value1 = df['a'][0]\n"
            "value2 = df['a'][1]\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.smell_detector.detect(tree, extracted_data, self.filename)
        self.assertEqual(len(result), 2)  # Two smells should be detected
        self.assertEqual(result[0]["line"], 3)  # Line of the first smell
        self.assertEqual(result[1]["line"], 4)  # Line of the second smell


if __name__ == "__main__":
    unittest.main()
