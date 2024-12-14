import os
import shutil
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from components.project_analyzer import ProjectAnalyzer


class TestProjectAnalyzer(unittest.TestCase):

    def tearDown(self):
        # Check if output path is defined and exists

        if os.path.exists("test/unit_testing/cli/mock_output_path"):
            try:
                shutil.rmtree("test/unit_testing/cli/mock_output_path")
            except Exception as e:
                print(
                    f"Failed to delete test/unit_testing/cli/mock_output. Reason: {e}"
                )

    @patch("os.listdir")
    @patch("cli.file_utils.FileUtils.get_python_files")
    @patch("components.inspector.Inspector.inspect")
    def test_analyze_project(self, mock_inspect, mock_get_python_files, mock_listdir):
        # Setup mocks
        mock_get_python_files.return_value = ["file1.py", "file2.py"]
        mock_inspect.side_effect = [
            pd.DataFrame(
                {
                    "filename": ["file1.py"],
                    "function_name": ["func1"],
                    "smell_name": ["smell1"],
                    "line": [10],
                    "description": ["desc1"],
                    "additional_info": ["info1"],
                }
            ),
            pd.DataFrame(
                {
                    "filename": ["file2.py"],
                    "function_name": ["func2"],
                    "smell_name": ["smell2"],
                    "line": [20],
                    "description": ["desc2"],
                    "additional_info": ["info2"],
                }
            ),
        ]

        project_analyzer = ProjectAnalyzer(
            output_path="test/unit_testing/cli/mock_output_path"
        )
        total_smells = project_analyzer.analyze_project("mock_project_path")

        # Assertions
        self.assertEqual(total_smells, 2)
        mock_get_python_files.assert_called_once_with("mock_project_path")
        mock_inspect.assert_any_call("file1.py")
        mock_inspect.assert_any_call("file2.py")

    @patch("os.listdir")
    @patch("cli.file_utils.FileUtils.get_python_files")
    @patch("components.inspector.Inspector.inspect")
    def test_analyze_projects_sequential(
        self, mock_inspect, mock_get_python_files, mock_listdir
    ):
        # Setup mocks
        mock_listdir.return_value = ["project1", "project2"]
        mock_get_python_files.return_value = ["file1.py", "file2.py"]
        mock_inspect.side_effect = [
            pd.DataFrame(
                {
                    "filename": ["file1.py"],
                    "function_name": ["func1"],
                    "smell_name": ["smell1"],
                    "line": [10],
                    "description": ["desc1"],
                    "additional_info": ["info1"],
                }
            ),
            pd.DataFrame(
                {
                    "filename": ["file2.py"],
                    "function_name": ["func2"],
                    "smell_name": ["smell2"],
                    "line": [20],
                    "description": ["desc2"],
                    "additional_info": ["info2"],
                }
            ),
        ]

        project_analyzer = ProjectAnalyzer(
            output_path="test/unit_testing/cli/mock_output_path"
        )

        with patch("builtins.print") as mock_print:
            project_analyzer.analyze_projects_sequential("mock_base_path", resume=False)

        # Assertions
        mock_listdir.assert_called_once_with("mock_base_path")
        mock_print.assert_any_call("Analyzing project 'project1' sequentially...")
        mock_print.assert_any_call("Analyzing project 'project2' sequentially...")
        mock_print.assert_any_call(unittest.mock.ANY)

    @patch("os.listdir")
    @patch("concurrent.futures.ThreadPoolExecutor.submit")
    @patch("cli.file_utils.FileUtils.get_python_files")
    @patch("components.inspector.Inspector.inspect")
    def test_analyze_projects_parallel(
        self, mock_inspect, mock_get_python_files, mock_submit, mock_listdir
    ):
        # Setup mocks
        mock_listdir.return_value = ["project1", "project2"]
        mock_get_python_files.return_value = ["file1.py", "file2.py"]
        mock_inspect.return_value = pd.DataFrame(
            {
                "filename": ["file1.py", "file2.py"],
                "function_name": ["func1", "func2"],
                "smell_name": ["smell1", "smell2"],
                "line": [10, 20],
                "description": ["desc1", "desc2"],
                "additional_info": ["info1", "info2"],
            }
        )
        mock_future = MagicMock()  # Mock the returned future object
        mock_submit.return_value = mock_future

        project_analyzer = ProjectAnalyzer(
            output_path="test/unit_testing/cli/mock_output_path"
        )

        with patch("builtins.print") as mock_print:
            project_analyzer.analyze_projects_parallel(
                base_path="mock_base_path", max_workers=2
            )

        # Assertions
        mock_listdir.assert_called_once_with("mock_base_path")
        mock_print.assert_any_call(unittest.mock.ANY)

        # Check the calls to submit
        submitted_calls = mock_submit.call_args_list

        # Verify the callable and arguments for each project
        self.assertEqual(len(submitted_calls), 2)
        self.assertEqual(
            submitted_calls[0][0][1], "project1"
        )  # Second argument of the first call
        self.assertEqual(
            submitted_calls[1][0][1], "project2"
        )  # Second argument of the second call

        # Verify the callable function is as expected
        for call in submitted_calls:
            self.assertTrue(call[0][0].__name__, "analyze_and_count_smells")

    @patch("os.listdir")
    @patch("cli.file_utils.FileUtils.get_python_files")
    @patch("components.inspector.Inspector.inspect")
    def test_projects_analysis_sequential(
        self, mock_inspect, mock_get_python_files, mock_listdir
    ):
        # Setup mocks
        mock_listdir.return_value = ["project1", "project2"]
        mock_get_python_files.return_value = ["file1.py", "file2.py"]
        mock_inspect.side_effect = [
            pd.DataFrame(
                {
                    "filename": ["file1.py"],
                    "function_name": ["func1"],
                    "smell_name": ["smell1"],
                    "line": [10],
                    "description": ["desc1"],
                    "additional_info": ["info1"],
                }
            ),
            pd.DataFrame(
                {
                    "filename": ["file2.py"],
                    "function_name": ["func2"],
                    "smell_name": ["smell2"],
                    "line": [20],
                    "description": ["desc2"],
                    "additional_info": ["info2"],
                }
            ),
        ]

        project_analyzer = ProjectAnalyzer(
            output_path="test/unit_testing/cli/mock_output_path"
        )

        with patch("builtins.print") as mock_print:
            project_analyzer.projects_analysis(
                base_path="mock_base_path", parallel=False
            )

        # Assertions
        mock_listdir.assert_called_once_with("mock_base_path")
        mock_print.assert_any_call(unittest.mock.ANY)

    @patch("os.listdir")
    @patch("cli.file_utils.FileUtils.get_python_files")
    @patch("components.inspector.Inspector.inspect")
    def test_projects_analysis_parallel(
        self, mock_inspect, mock_get_python_files, mock_listdir
    ):
        # Setup mocks
        mock_listdir.return_value = ["project1", "project2"]
        mock_get_python_files.return_value = ["file1.py", "file2.py"]
        mock_inspect.return_value = pd.DataFrame(
            {
                "filename": ["file1.py", "file2.py"],
                "function_name": ["func1", "func2"],
                "smell_name": ["smell1", "smell2"],
                "line": [10, 20],
                "description": ["desc1", "desc2"],
                "additional_info": ["info1", "info2"],
            }
        )

        project_analyzer = ProjectAnalyzer(
            output_path="test/unit_testing/cli/mock_output_path"
        )

        with patch("builtins.print") as mock_print:
            project_analyzer.projects_analysis(
                base_path="mock_base_path", parallel=True
            )

        # Assertions
        mock_listdir.assert_called_once_with("mock_base_path")
        mock_print.assert_any_call(unittest.mock.ANY)


if __name__ == "__main__":
    unittest.main()
