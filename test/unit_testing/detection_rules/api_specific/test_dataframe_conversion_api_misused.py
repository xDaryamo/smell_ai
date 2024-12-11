import unittest
import ast
from detection_rules.api_specific.dataframe_conversion_api_misused import (
    DataFrameConversionAPIMisused,
)


class TestDataFrameConversionAPIMisused(unittest.TestCase):

    def setUp(self):
        """
        Setup method to initialize the DataFrameConversionAPIMisused instance.
        """
        self.detector = DataFrameConversionAPIMisused()

    def test_detect_no_smell(self):
        """
        Test the detect method when no misuse
        of the `values` attribute is present.
        """
        code = (
            "import pandas as pd\n"
            "def no_smell():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    value = df.loc[0, 'a']\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell(self):
        """
        Test the detect method when gradients are \
        not cleared before backward propagation.
        """
        code = (
            "import torch\n"
            "def train():\n"
            "    optimizer = torch.optim.SGD([], lr=0.01)\n"
            "    for epoch in range(10):\n"
            "        loss = torch.tensor(0.0, requires_grad=True)\n"
            "        loss.backward()\n"
        )
        tree = ast.parse(code)

        for node in ast.walk(tree):
            print(ast.dump(node))

        extracted_data = {
            "libraries": {"torch": "torch"},
            "variables": ["optimizer"],
            "lines": {
                4: "for epoch in range(10):",
                5: "loss = torch.tensor(0.0, requires_grad=True)",
                6: "loss.backward()",
            },
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertIn(
            "`zero_grad()` not called before `backward()`",
            result[0]["additional_info"],
        )
        self.assertEqual(result[0]["line"], 6)  # Line where the smell occurs

    def test_detect_without_pandas_library(self):
        """
        Test the detect method when the pandas library is not imported.
        """
        code = (
            "def no_pandas():\n"
            "    df = {'a': [1, 2, 3]}\n"
            "    value = df['a'][0]\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No pandas alias
            "dataframe_variables": [],
        }

        result = self.detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_multiple_smells(self):
        """
        Test the detect method when multiple
        misuses of the `values` attribute are present.
        """
        code = (
            "import pandas as pd\n"
            "def api_misused():\n"
            "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
            "    value1 = df.values\n"
            "    value2 = df.values\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"pandas": "pd"},
            "dataframe_variables": ["df"],
        }

        result = self.detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 2)  # Two smells should be detected
        self.assertEqual(result[0]["line"], 4)  # Line of the first smell
        self.assertEqual(result[1]["line"], 5)  # Line of the second smell


if __name__ == "__main__":
    unittest.main()
