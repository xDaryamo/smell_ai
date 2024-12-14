import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import pandas as pd
from io import StringIO

# Assuming FileUtils is in the module `your_module`
from cli.file_utils import FileUtils


class TestFileUtils(unittest.TestCase):

    def tearDown(self):
        # Check if output path is defined and exists

        if os.path.exists("test/unit_testing/cli/mock_output"):
            try:
                shutil.rmtree("test/unit_testing/cli/mock_output")
            except Exception as e:
                print(
                    f"Failed to delete test/unit_testing/cli/mock_output. Reason: {e}"
                )

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    def test_merge_results(
        self, mock_to_csv, mock_read_csv, mock_listdir, mock_exists, mock_makedirs
    ):
        # Mock setup
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.csv", "file2.csv"]

        # Mock the behavior of read_csv to return dataframes
        mock_read_csv.side_effect = [
            pd.DataFrame({"filename": ["file1"], "data": [1]}),
            pd.DataFrame({"filename": ["file2"], "data": [2]}),
        ]

        mock_to_csv.return_value = None

        # Call the function
        input_dir = "mock_input"
        output_dir = "test/unit_testing/cli/mock_output"
        FileUtils.merge_results(input_dir, output_dir)

        # Assert that correct calls were made
        mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
        mock_to_csv.assert_called_once_with(
            os.path.join(output_dir, "overview.csv"), index=False
        )

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    def test_merge_results_no_csv(
        self, mock_to_csv, mock_read_csv, mock_listdir, mock_exists, mock_makedirs
    ):
        # Mock setup: no CSV files
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt"]

        mock_read_csv.side_effect = []

        # Call the function
        input_dir = "mock_input"
        output_dir = "test/unit_testing/cli/mock_output"
        FileUtils.merge_results(input_dir, output_dir)

        # Assert no calls to to_csv as there are no valid CSVs
        mock_to_csv.assert_not_called()

    @patch("os.makedirs")
    @patch("os.walk")
    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    def test_merge_results(self, mock_to_csv, mock_read_csv, mock_walk, mock_makedirs):
        # Mock the os.walk behavior to simulate CSV files in the input directory
        mock_walk.return_value = [
            ("mock_input", [], ["file1.csv", "file2.csv"]),
        ]

        # Mock pandas.read_csv to return DataFrames for the CSV files
        mock_read_csv.side_effect = [
            pd.DataFrame({"filename": ["file1"], "data": [1]}),
            pd.DataFrame({"filename": ["file2"], "data": [2]}),
        ]

        input_dir = "mock_input"
        output_dir = "test/unit_testing/cli/mock_output"

        # Call the method under test
        FileUtils.merge_results(input_dir, output_dir)

        # Assert that os.makedirs was called to ensure the output directory exists
        mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)

        # Assert that pandas.DataFrame.to_csv was called to save the merged file
        mock_to_csv.assert_called_once_with(
            os.path.join(output_dir, "overview.csv"), index=False
        )

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("os.listdir")
    def test_clean_directory_create_folder(
        self, mock_listdir, mock_exists, mock_makedirs
    ):
        # Mock setup: directory does not exist
        mock_exists.return_value = False

        # Call the function
        root_path = "test/unit_testing/cli/mock_root"
        result = FileUtils.clean_directory(root_path)

        # Assert that the directory was created
        mock_makedirs.assert_called_once_with(os.path.join(root_path, "output"))
        self.assertEqual(result, os.path.join(root_path, "output"))

    @patch("os.walk")
    def test_get_python_files(self, mock_walk):
        # Mock the os.walk behavior
        mock_walk.return_value = [
            ("mock_path", ["venv", "lib"], ["file1.py", "file2.py", "file3.txt"])
        ]

        path = "test/unit_testing/cli/mock_path"
        result = FileUtils.get_python_files(path)

        self.assertEqual(
            result,
            [
                os.path.abspath(os.path.join("mock_path", "file1.py")),
                os.path.abspath(os.path.join("mock_path", "file2.py")),
            ],
        )

    @patch("os.walk")
    def test_get_python_files_with_venv(self, mock_walk):
        # Mock the os.walk behavior
        mock_walk.return_value = [
            ("mock_path", ["venv", "lib"], ["file1.py", "file2.py", "file3.txt"])
        ]

        path = "mock_path"
        result = FileUtils.get_python_files(path)

        expected = [
            os.path.abspath(os.path.join("mock_path", "file1.py")),
            os.path.abspath(os.path.join("mock_path", "file2.py")),
        ]
        self.assertEqual(result, expected)

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_get_python_files_no_files(self, mock_exists, mock_listdir):
        # Mock setup: no Python files
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt"]

        # Call the function
        path = "mock_path"
        result = FileUtils.get_python_files(path)

        # Assert that the result is an empty list
        self.assertEqual(result, [])

    @patch("os.walk")
    @patch("pandas.read_csv")
    @patch("pandas.DataFrame.to_csv")
    def test_merge_results_empty_dataframes(
        self, mock_to_csv, mock_read_csv, mock_walk
    ):
        mock_walk.return_value = [("mock_input", [], ["file1.csv", "file2.csv"])]
        mock_read_csv.side_effect = [
            pd.DataFrame(),  # Empty DataFrame
            pd.DataFrame({"filename": ["file2"], "data": [2]}),
        ]

        input_dir = "mock_input"
        output_dir = "test/unit_testing/cli/mock_output"

        FileUtils.merge_results(input_dir, output_dir)

        # Ensure empty CSV is skipped
        mock_to_csv.assert_called_once_with(
            os.path.join(output_dir, "overview.csv"), index=False
        )


if __name__ == "__main__":
    unittest.main()
