import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
import sys


class ReportGenerator:
    def __init__(
        self, input_file: str = "overview_output.csv", output_path: str = "."
    ):
        """
        Initializes the ReportGenerator with input and output file paths.

        Parameters:
        - input_file (str): The path to the input CSV file containing
          the overview data.
        - output_path (str): The directory where the reports will be saved.
        """
        self.input_file = input_file
        self.output_path = output_path

    def _load_data(self, file_format: str = "csv"):
        """
        Loads the data from the input file, supporting multiple formats.

        Parameters:
        - file_format (str): The format of the input file
          ('csv', 'json', 'excel').

        Returns:
        - pd.DataFrame: The DataFrame containing the loaded data.
        """
        if file_format == "csv":
            return pd.read_csv(self.input_file)
        elif file_format == "json":
            return pd.read_json(self.input_file)
        elif file_format == "excel":
            return pd.read_excel(self.input_file)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def smell_report(self):
        """Generates a general overview report."""
        df = self._load_data()
        df = df[["smell_name", "filename"]]
        report = (
            df.groupby("smell_name")
            .count()
            .rename(columns={"filename": "occurrences"})
        )
        report.to_csv(os.path.join(self.output_path, "general_overview.csv"))
        print("General smell report saved to 'general_overview.csv'.")

    def project_report(self):
        """Generates a project-specific report treating files as
        part of separate projects based on their paths."""
        df = self._load_data()

        # Normalize paths and extract the project name
        project_names = []
        for filepath in df["filename"]:
            normalized_path = os.path.normpath(
                filepath
            )  # Normalize path for cross-platform compatibility
            project_name = os.path.basename(os.path.dirname(normalized_path))
            if not project_name:  # Handle root-level files
                project_name = "root"
            project_names.append(project_name)

        df["project_name"] = project_names

        # Generate the report
        report = (
            df.groupby("project_name").size().reset_index(name="total_smells")
        )

        output_file = os.path.join(self.output_path, "project_overview.csv")
        report.to_csv(output_file, index=False)

        print(f"Project-specific report saved to '{output_file}'.")

    def summary_report(self):
        """
        Generates a summary report with:
        - General overview of code smells.
        - Per-project summary of total smells.
        - Detailed sheets for each project specifying
        each smell and its occurrences.
        """
        df = self._load_data()

        project_names = []
        for filepath in df["filename"]:
            project_name = os.path.basename(os.path.dirname(filepath))
            if project_name == "":
                project_name = "SingleProject"
            project_names.append(project_name)

        df["project_name"] = project_names

        general_report = (
            df[["smell_name", "filename"]]
            .groupby("smell_name")
            .count()
            .rename(columns={"filename": "occurrences"})
        )

        project_summary = (
            df.groupby("project_name").size().reset_index(name="total_smells")
        )

        with pd.ExcelWriter(
            os.path.join(self.output_path, "summary_report.xlsx"),
            engine="openpyxl",
        ) as writer:
            # Write the general overview
            general_report.to_excel(
                writer, sheet_name="General Overview", index=True
            )

            # Write the per-project summary
            project_summary.to_excel(
                writer, sheet_name="Project Overview", index=False
            )

            # Write a detailed sheet for each project
            for project_name, project_df in df.groupby("project_name"):
                project_details = (
                    project_df.groupby("smell_name")
                    .size()
                    .reset_index(name="occurrences")
                )
                # Write the project-specific sheet
                sanitized_sheet_name = project_name[
                    :30
                ]  # Excel sheet names must be <= 31 chars
                project_details.to_excel(
                    writer, sheet_name=sanitized_sheet_name, index=False
                )

        print("Summary report saved to 'summary_report.xlsx'.")

    def visualize_smell_report(self):
        """Generates a bar chart for the general smell overview."""
        df = self._load_data()
        df = df[["smell_name", "filename"]]
        report = (
            df.groupby("smell_name")
            .count()
            .rename(columns={"filename": "occurrences"})
        )

        report.plot(kind="bar", legend=False)
        plt.title("Smell Occurrences by Type")
        plt.xlabel("Smell Type")
        plt.ylabel("Number of Occurrences")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_path, "smell_report_chart.png"))
        print("Bar chart saved to 'smell_report_chart.png'.")

    def cleanup_old_reports(self):
        """Cleans up old reports in the output directory."""
        for file in os.listdir(self.output_path):
            if (
                file.endswith(".csv")
                or file.endswith(".xlsx")
                or file.endswith(".png")
            ) and file != "overview.csv":
                os.remove(os.path.join(self.output_path, file))
        print("Old reports cleaned up from the output directory.")

    def menu(self):
        """Displays a menu for the user to choose which report to generate."""
        print("Select which reports to generate:")
        print("1. General Smell Report")
        print("2. Project-Specific Report")
        print("3. Both Reports")
        print("4. Plot Report")
        print("5. Summary .xlsx Report")
        print("6. Clean-up Old Reports")
        choice = input("Enter your choice: ")
        return choice


def main():
    parser = argparse.ArgumentParser(
        description="Generate reports for code smell analysis."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input CSV file (e.g., overview_output.csv).",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Directory to save the reports.",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(args.output):
        os.makedirs(args.output, exist_ok=True)

    generator = ReportGenerator(input_file=args.input, output_path=args.output)

    try:
        choice = generator.menu()
        if choice == "1":
            generator.smell_report()
        elif choice == "2":
            generator.project_report()
        elif choice == "3":
            generator.smell_report()
            generator.project_report()
        elif choice == "4":
            generator.visualize_smell_report()
        elif choice == "5":
            generator.summary_report()
        elif choice == "6":
            generator.cleanup_old_reports()
        else:
            print("Invalid choice. Exiting.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
