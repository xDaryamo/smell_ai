import unittest
import ast
from detection_rules.generic.deterministic_algorithm_option_not_used import (  # noqa: E501
    DeterministicAlgorithmOptionSmell,
)


class TestDeterministicAlgorithmOptionSmell(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize the
        DeterministicAlgorithmOptionSmell instance.
        """
        self.smell_detector = DeterministicAlgorithmOptionSmell()

    def test_detect_no_smell(self):
        """
        Test the detect method when no misuse of
        `use_deterministic_algorithms` is present.
        """
        code = (
            "import torch\n"
            "def main():\n"
            "    x = torch.tensor([1, 2, 3])\n"
            "    y = torch.mean(x)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"torch": "torch"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_smell(self):
        """
        Test the detect method when
        `use_deterministic_algorithms(True)` is used.
        """
        code = (
            "import torch\n"
            "def main():\n"
            "    torch.use_deterministic_algorithms(True)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"torch": "torch"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(
            result[0]["name"], "deterministic_algorithm_option_not_used"
        )
        self.assertIn(
            "Using `torch.use_deterministic_algorithms(True)`",
            result[0]["additional_info"],
        )
        self.assertEqual(result[0]["line"], 3)  # Line where the smell occurs

    def test_detect_without_torch_library(self):
        """
        Test the detect method when the PyTorch library is not imported.
        """
        code = (
            "\n"
            "def main():\n"
            "\n"
            "    th.use_deterministic_algorithms(True)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {},  # No PyTorch alias
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 0)  # No smells should be detected

    def test_detect_with_alias(self):
        """
        Test the detect method when PyTorch is imported with
        an alias and `use_deterministic_algorithms(True)` is used.
        """
        code = (
            "import torch as th\n"
            "def main():\n"
            "    th.use_deterministic_algorithms(True)\n"
        )
        tree = ast.parse(code)
        extracted_data = {
            "libraries": {"torch": "th"},
        }

        result = self.smell_detector.detect(tree, extracted_data)
        self.assertEqual(len(result), 1)  # One smell should be detected
        self.assertEqual(
            result[0]["name"], "deterministic_algorithm_option_not_used"
        )
        self.assertIn(
            "Using `torch.use_deterministic_algorithms(True)`",
            result[0]["additional_info"],
        )
        self.assertEqual(result[0]["line"], 3)  # Line where the smell occurs


if __name__ == "__main__":
    unittest.main()
