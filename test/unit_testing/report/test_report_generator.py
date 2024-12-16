import os
import pandas as pd
import matplotlib.pyplot as plt


class ReportGenerator:
    """
    A class to generate various types of reports and visualizations
    based on code smell data.
    """

    def __init__(self, input_path, output_path):
        """
        Initialize the ReportGenerator with input and output paths.
        """
        self.input_path = os.path.abspath(input_path)
        self.output_path = os.path.abspath(output_path)

    def _get_output_path(self, filename):
        """
        Generate a normalized output file path.
        """
        return os.path.normpath(os.path.join(self.output_path, filename))

    def smell_report(self, data):
        """
        Generate and save a general smell report as a CSV file.
        """
        output_path = self._get_output_path("general_overview.csv")
        data.to_csv(output_path, index=False)
        print(f"General smell report saved to '{output_path}'.")

    def project_report(self, data):
        """
        Generate and save a project-specific report as a CSV file.
        """
        output_path = self._get_output_path("project_overview.csv")
        data.to_csv(output_path, index=False)
        print(f"Project-specific report saved to '{output_path}'.")

    def summary_report(self, data):
        """
        Generate and save a summary report in Excel format.
        """
        output_path = self._get_output_path("summary_report.xlsx")
        with pd.ExcelWriter(output_path) as writer:
            data.to_excel(writer, sheet_name="Summary", index=False)
        print(f"Summary report saved to '{output_path}'.")

    def visualize_smell_report(self, data):
        """
        Generate a bar chart showing the distribution of code smells
        and save it as a PNG file.
        """
        output_path = self._get_output_path("smell_report_chart.png")
        data["smell_name"].value_counts().plot(kind="bar")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Bar chart saved to '{output_path}'.")

    def menu(self):
        """
        Display a menu for the user to select options.
        """
        print("1. Generate Smell Report")
        print("2. Generate Project Report")
        print("3. Generate Summary Report")
        print("4. Visualize Smell Report")
        print("5. Exit")
        choice = input("Enter your choice: ")
        return choice
