import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from code_extractor.model_extractor import ModelExtractor


class TestModelExtractor(unittest.TestCase):

    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_load_model_dict(self, mock_exists, mock_read_csv):
        """Test loading the model dictionary from a CSV file."""
        # Setup mock
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.columns = ["method", "library"]
        mock_df.to_dict.return_value = {"method": ["method1"], "library": ["lib1"]}
        mock_read_csv.return_value = mock_df

        extractor = ModelExtractor("models.csv", "tensors.csv")
        model_dict = extractor.load_model_dict()

        self.assertEqual(model_dict, {"method": ["method1"], "library": ["lib1"]})
        mock_exists.assert_called_once_with("models.csv")
        mock_read_csv.assert_called_once_with("models.csv")

    @patch("os.path.exists")
    def test_load_model_dict_file_not_found(self, mock_exists):
        """Test that FileNotFoundError is raised when model file doesn't exist."""
        mock_exists.return_value = False

        extractor = ModelExtractor("models.csv", "tensors.csv")
        with self.assertRaises(FileNotFoundError):
            extractor.load_model_dict()

    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_load_model_dict_missing_columns(self, mock_exists, mock_read_csv):
        """Test that ValueError is raised
        if the expected columns are missing."""
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.columns = ["other_column"]
        mock_read_csv.return_value = mock_df

        extractor = ModelExtractor("models.csv", "tensors.csv")
        with self.assertRaises(ValueError):
            extractor.load_model_dict()

    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_load_tensor_operations_dict(self, mock_exists, mock_read_csv):
        """Test loading the tensor operations dictionary from a CSV file."""
        mock_exists.return_value = True

        # Creating a mock DataFrame
        df = pd.DataFrame(
            {"number_of_tensors_input": [2, 1], "operation": ["op1", "op2"]}
        )

        mock_read_csv.return_value = df

        # Initialize the ModelExtractor
        extractor = ModelExtractor("models.csv", "tensors.csv")

        # Load tensor operations dictionary
        tensor_dict = extractor.load_tensor_operations_dict()

        # Expected output: only operations with more than one tensor input
        expected_dict = {"number_of_tensors_input": [2], "operation": ["op1"]}

        self.assertEqual(tensor_dict, expected_dict)
        mock_exists.assert_called_once_with("tensors.csv")
        mock_read_csv.assert_called_once_with("tensors.csv")

    @patch("os.path.exists")
    def test_load_tensor_operations_dict_file_not_found(self, mock_exists):
        """Test that FileNotFoundError is raised when tensor operations file doesn't exist."""
        mock_exists.return_value = False

        extractor = ModelExtractor("models.csv", "tensors.csv")
        with self.assertRaises(FileNotFoundError):
            extractor.load_tensor_operations_dict()

    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_load_tensor_operations_dict_missing_columns(
        self, mock_exists, mock_read_csv
    ):
        """Test that ValueError is raised if the expected columns are missing in tensor operations CSV."""
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.columns = ["other_column"]
        mock_read_csv.return_value = mock_df

        extractor = ModelExtractor("models.csv", "tensors.csv")
        with self.assertRaises(ValueError):
            extractor.load_tensor_operations_dict()

    def test_load_model_methods(self):
        """Test extracting model methods."""
        extractor = ModelExtractor("models.csv", "tensors.csv")
        extractor.model_dict = {
            "method": ["method1", "method2"],
            "library": ["lib1", "lib2"],
        }

        methods = extractor.load_model_methods()
        self.assertEqual(methods, ["method1", "method2"])

    def test_load_model_methods_not_loaded(self):
        """Test that ValueError is raised if model dictionary is not loaded."""
        extractor = ModelExtractor("models.csv", "tensors.csv")
        with self.assertRaises(ValueError):
            extractor.load_model_methods()

    def test_check_model_method(self):
        """Test checking if a model belongs to a library."""
        extractor = ModelExtractor("models.csv", "tensors.csv")
        extractor.model_dict = {
            "method": ["method1", "method2"],
            "library": ["lib1", "lib2"],
        }

        result = extractor.check_model_method("method1", ["lib1"])
        self.assertTrue(result)

    def test_check_model_method_not_in_library(self):
        """Test that check_model_method returns False if model is not in the specified library."""
        extractor = ModelExtractor("models.csv", "tensors.csv")
        extractor.model_dict = {
            "method": ["method1", "method2"],
            "library": ["lib1", "lib2"],
        }

        result = extractor.check_model_method("method1", ["lib2"])
        self.assertFalse(result)

    def test_check_model_method_not_loaded(self):
        """Test that ValueError is raised if model dictionary is not loaded."""
        extractor = ModelExtractor("models.csv", "tensors.csv")
        with self.assertRaises(ValueError):
            extractor.check_model_method("method1", ["lib1"])


if __name__ == "__main__":
    unittest.main()
