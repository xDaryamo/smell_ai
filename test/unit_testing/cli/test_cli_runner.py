import shutil
import unittest
from unittest.mock import patch, MagicMock
import unittest.mock
from cli.cli_runner import CodeSmileCLI
import argparse
import os

from cli.file_utils import FileUtils
from cli.project_analyzer import ProjectAnalyzer


class TestCodeSmileCLI(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace(
            input="mock_input",
            output="test/unit_testing/cli/mock_output",
            parallel=False,
            resume=False,
            multiple=False,
            max_workers=5,
        )

    def tearDown(self):
        # Check if output path is defined and exists
        if self.args.output:
            if os.path.exists(self.args.output):
                try:
                    shutil.rmtree(self.args.output)
                except Exception as e:
                    print(f"Failed to delete {self.args.output}. Reason: {e}")
        else:
            print("No output directory to clean up.")

    @patch("cli.file_utils.FileUtils.clean_directory")
    @patch("cli.file_utils.FileUtils.merge_results")
    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_project")
    @patch("builtins.print")
    def test_single_project_analysis(
        self, mock_print, mock_analyze_project, mock_merge_results, mock_clean_directory
    ):
        # Set up mock return value for clean_directory
        mock_clean_directory.return_value = "test/unit_testing/cli/mock_output_cleaned"
        mock_analyze_project.return_value = 3  # Simulate 3 code smells found

        cli = CodeSmileCLI(self.args)
        cli.execute()

        # Assertions
        mock_clean_directory.assert_called_once_with(
            "test/unit_testing/cli/mock_output", "output"
        )
        mock_analyze_project.assert_called_once_with("mock_input")
        mock_merge_results.assert_called_once_with(
            "test/unit_testing/cli/mock_output_cleaned",
            os.path.join("test/unit_testing/cli/mock_output_cleaned", "overview"),
        )
        mock_print.assert_any_call(
            "Starting analysis with the following configuration:"
        )
        mock_print.assert_any_call("Analysis completed. Total code smells found: 3")

    @patch("cli.file_utils.FileUtils.clean_directory")
    @patch("cli.file_utils.FileUtils.merge_results")
    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_projects_parallel")
    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_projects_sequential")
    @patch("builtins.print")
    def test_multiple_projects_analysis_parallel(
        self,
        mock_print,
        mock_analyze_projects_sequential,
        mock_analyze_projects_parallel,
        mock_clean_directory,
        mock_merge_results,
    ):
        self.args.multiple = True
        self.args.parallel = True

        # Set up mock return value for clean_directory
        mock_clean_directory.return_value = "test/unit_testing/cli/mock_output_cleaned"

        cli = CodeSmileCLI(self.args)
        cli.execute()

        # Assertions
        mock_clean_directory.assert_called_once_with(
            unittest.mock.ANY, unittest.mock.ANY
        )
        mock_analyze_projects_parallel.assert_called_once_with("mock_input", 5)
        mock_analyze_projects_sequential.assert_not_called()
        mock_merge_results.assert_called_once_with(
            "test/unit_testing/cli/mock_output", "output"
        )
        mock_print.assert_any_call(
            "Starting analysis with the following configuration:"
        )

    @patch("cli.file_utils.FileUtils.clean_directory")
    @patch("cli.file_utils.FileUtils.merge_results")
    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_projects_sequential")
    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_projects_parallel")
    @patch("builtins.print")
    def test_multiple_projects_analysis_sequential(
        self,
        mock_print,
        mock_analyze_projects_parallel,
        mock_analyze_projects_sequential,
        mock_clean_directory,
        mock_merge_results,
    ):
        self.args.multiple = True
        self.args.parallel = False

        # Set up mock return value for clean_directory
        mock_clean_directory.return_value = "test/unit_testing/cli/mock_output_cleaned"

        cli = CodeSmileCLI(self.args)
        cli.execute()

        # Assertions
        mock_clean_directory.assert_called_once_with(
            unittest.mock.ANY, unittest.mock.ANY
        )
        mock_analyze_projects_sequential.assert_called_once_with(
            "mock_input", resume=False
        )
        mock_analyze_projects_parallel.assert_not_called()
        mock_merge_results.assert_called_once_with(
            "test/unit_testing/cli/mock_output", "output"
        )
        mock_print.assert_any_call(
            "Starting analysis with the following configuration:"
        )

    @patch("builtins.print")
    def test_missing_input(self, mock_print):
        self.args.input = None

        with self.assertRaises(SystemExit):
            cli = CodeSmileCLI(self.args)
            cli.execute()

        mock_print.assert_any_call(
            "Error: Please specify both input and output folders."
        )

    @patch("builtins.print")
    def test_missing_output_argument(self, mock_print):
        self.args.output = None

        with self.assertRaises(SystemExit):
            cli = CodeSmileCLI(self.args)
            cli.execute()

        mock_print.assert_any_call(
            "Error: Please specify both input and output folders."
        )

    def test_invalid_max_workers(self):
        self.args.parallel = True
        self.args.multiple = True
        self.args.max_workers = 0

        with self.assertRaises(ValueError) as context:
            cli = CodeSmileCLI(self.args)
            cli.execute()

        self.assertEqual(str(context.exception), "max_workers must be greater than 0.")

    @patch("cli.file_utils.FileUtils.merge_results")
    @patch("builtins.print")
    def test_merge_results_invalid_path(self, mock_print, mock_merge_results):
        # Simulate FileNotFoundError during merge_results
        mock_merge_results.side_effect = FileNotFoundError("Invalid path")

        cli = CodeSmileCLI(self.args)

        with self.assertRaises(FileNotFoundError):
            cli.execute()

        # Ensure that the success message is NOT printed
        calls = [
            call[0][0] for call in mock_print.call_args_list
        ]  # Extract printed messages
        self.assertNotIn("Analysis results saved successfully.", calls)

        # Optionally, assert the expected error message or handling
        mock_print.assert_any_call(
            "Starting analysis with the following configuration:"
        )

    @patch("builtins.print")
    def test_multiple_projects_parallel_missing_input(self, mock_print):
        self.args.input = None
        self.args.multiple = True
        self.args.parallel = True

        with self.assertRaises(SystemExit):
            cli = CodeSmileCLI(self.args)
            cli.execute()

        mock_print.assert_any_call(
            "Error: Please specify both input and output folders."
        )

    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_projects_sequential")
    @patch("builtins.print")
    def test_multiple_projects_sequential_with_resume(
        self, mock_print, mock_analyze_sequential
    ):
        self.args.multiple = True
        self.args.resume = True
        self.args.parallel = False

        cli = CodeSmileCLI(self.args)
        cli.execute()

        mock_analyze_sequential.assert_called_once_with("mock_input", resume=True)
        mock_print.assert_any_call("Resume execution: True")

    @patch("cli.project_analyzer.ProjectAnalyzer.analyze_project")
    @patch("builtins.print")
    def test_analyze_project_failure(self, mock_print, mock_analyze_project):
        mock_analyze_project.side_effect = Exception("Analysis failed")

        cli = CodeSmileCLI(self.args)

        with self.assertRaises(Exception):
            cli.execute()

        mock_print.assert_any_call(
            "Starting analysis with the following configuration:"
        )

    @patch("cli.file_utils.FileUtils.clean_directory")
    @patch("builtins.print")
    def test_output_directory_cleanup_failure(self, mock_print, mock_clean_directory):
        # Simulate PermissionError during clean_directory
        mock_clean_directory.side_effect = PermissionError("Permission denied")

        cli = CodeSmileCLI(self.args)

        with self.assertRaises(PermissionError):
            cli.execute()

        # Ensure that the error message is logged or handled appropriately
        mock_print.assert_any_call(
            "Starting analysis with the following configuration:"
        )

        # Check that the program does not print the success message
        calls = [
            call[0][0] for call in mock_print.call_args_list
        ]  # Extract printed messages
        self.assertNotIn("Analysis results saved successfully.", calls)

    @patch("builtins.print")
    def test_log_messages(self, mock_print):
        cli = CodeSmileCLI(self.args)
        cli.execute()

        expected_calls = [
            unittest.mock.call("Starting analysis with the following configuration:"),
            unittest.mock.call("Input folder: mock_input"),
            unittest.mock.call("Output folder: test/unit_testing/cli/mock_output"),
            unittest.mock.call("Parallel execution: False"),
            unittest.mock.call("Resume execution: False"),
            unittest.mock.call("Analyze multiple projects: False"),
        ]

        mock_print.assert_has_calls(expected_calls, any_order=False)

    @patch("cli.cli_runner.CodeSmileCLI.execute")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_function(self, mock_parse_args, mock_execute):
        mock_args = argparse.Namespace(
            input="mock_input",
            output="test/unit_testing/cli/mock_output",
            parallel=False,
            resume=False,
            multiple=False,
            max_workers=5,
        )
        mock_parse_args.return_value = mock_args

        with patch("builtins.print"):
            from cli.cli_runner import main

            main()

        mock_parse_args.assert_called_once()
        mock_execute.assert_called_once()
