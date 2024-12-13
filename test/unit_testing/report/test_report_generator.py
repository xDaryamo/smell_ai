import unittest
import pandas as pd
import os
import shutil
from report.report_generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a temporary input CSV file and output directory."""
        cls.input_file = "test_overview_output.csv"
        cls.output_path = "test_reports"

        # Create test input CSV file
        data = {
            "filename": [
                "C:\\project1\\file1.py",
                "C:\\project1\\file2.py",
                "C:\\project2\\file1.py",
                "C:\\project2\\file2.py",
                "/home/user/project3/file1.py",
                "/home/user/project3/file2.py",
                "/project4/file1.py",
                "/project4/file2.py",
            ],
            "function_name": [
                "main",
                "func1",
                "func2",
                "func3",
                "main",
                "func1",
                "func2",
                "func3",
            ],
            "smell_name": [
                "smell1",
                "smell2",
                "smell1",
                "smell3",
                "smell1",
                "smell2",
                "smell1",
                "smell3",
            ],
            "line": [10, 20, 30, 40, 50, 60, 70, 80],
            "description": [
                "Description of smell1",
                "Description of smell2",
                "Description of smell1",
                "Description of smell3",
                "Description of smell1",
                "Description of smell2",
                "Description of smell1",
                "Description of smell3",
            ],
            "additional_info": [
                "Info1",
                "Info2",
                "Info3",
                "Info4",
                "Info5",
                "Info6",
                "Info7",
                "Info8",
            ],
        }
        df = pd.DataFrame(data)
        df.to_csv(cls.input_file, index=False)

        # Create output directory
        os.makedirs(cls.output_path, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files and directories."""
        if os.path.exists(cls.input_file):
            os.remove(cls.input_file)
        if os.path.exists(cls.output_path):
            shutil.rmtree(cls.output_path)

    def setUp(self):
        self.generator = ReportGenerator(
            input_file=self.input_file, output_path=self.output_path
        )

    def test_smell_report(self):
        """Test the smell_report method."""
        self.generator.smell_report()
        output_file = os.path.join(self.output_path, "general_overview.csv")
        self.assertTrue(os.path.exists(output_file))

        df = pd.read_csv(output_file)
        self.assertListEqual(
            df.columns.tolist(), ["smell_name", "occurrences"]
        )
        self.assertEqual(len(df), 3)

    def test_project_report(self):
        """Test the project_report method."""
        self.generator.project_report()
        output_file = os.path.join(self.output_path, "project_overview.csv")
        self.assertTrue(os.path.exists(output_file))

        df = pd.read_csv(output_file)
        self.assertListEqual(
            df.columns.tolist(), ["project_name", "total_smells"]
        )

        # Verify the number of projects
        self.assertEqual(len(df), 4)

        # Verify the project names and total smells
        expected_data = {
            "project_name": ["project1", "project2", "project3", "project4"],
            "total_smells": [2, 2, 2, 2],
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(
            df.sort_values(by="project_name").reset_index(drop=True),
            expected_df.sort_values(by="project_name").reset_index(drop=True),
        )

    def test_summary_report(self):
        """Test the summary_report method."""
        self.generator.summary_report()
        output_file = os.path.join(self.output_path, "summary_report.xlsx")
        self.assertTrue(os.path.exists(output_file))

        with pd.ExcelFile(output_file) as xls:
            sheets = xls.sheet_names
            self.assertIn("General Overview", sheets)
            self.assertIn("Project Overview", sheets)

            general_overview = pd.read_excel(
                xls, sheet_name="General Overview"
            )
            project_overview = pd.read_excel(
                xls, sheet_name="Project Overview"
            )

            self.assertListEqual(
                general_overview.columns.tolist(),
                ["smell_name", "occurrences"],
            )
            self.assertListEqual(
                project_overview.columns.tolist(),
                ["project_name", "total_smells"],
            )

    def test_visualize_smell_report(self):
        """Test the visualize_smell_report method."""
        self.generator.visualize_smell_report()
        output_file = os.path.join(self.output_path, "smell_report_chart.png")
        self.assertTrue(os.path.exists(output_file))

    def test_cleanup_old_reports(self):
        """Test the cleanup_old_reports method."""
        # Create dummy report files
        dummy_files = ["file1.csv", "file2.xlsx", "file3.png"]
        for file in dummy_files:
            with open(os.path.join(self.output_path, file), "w") as f:
                f.write("dummy content")

        self.generator.cleanup_old_reports()

        for file in dummy_files:
            self.assertFalse(
                os.path.exists(os.path.join(self.output_path, file))
            )


if __name__ == "__main__":
    unittest.main()
