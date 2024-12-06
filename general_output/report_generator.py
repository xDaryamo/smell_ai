import pandas as pd
import matplotlib.pyplot as plt
import os

class ReportGenerator:
    def __init__(self, input_file: str = 'overview_output.csv', output_path: str = '.'):
        """
        Initializes the ReportGenerator with input and output file paths.

        Parameters:
        - input_file (str): The path to the input CSV file containing the overview data.
        - output_path (str): The directory where the reports will be saved.
        """
        self.input_file = input_file
        self.output_path = output_path

    def _load_data(self, file_format: str = 'csv'):
        """
        Loads the data from the input file, supporting multiple formats.

        Parameters:
        - file_format (str): The format of the input file ('csv', 'json', 'excel').

        Returns:
        - pd.DataFrame: The DataFrame containing the loaded data.
        """
        if file_format == 'csv':
            return pd.read_csv(self.input_file)
        elif file_format == 'json':
            return pd.read_json(self.input_file)
        elif file_format == 'excel':
            return pd.read_excel(self.input_file)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def smell_report(self):
        """
        Generates a general overview report of the code smells, grouped by the name of the smell.

        Returns:
        - None
        """
        df = self._load_data()

        # Filter the dataframe to include only the necessary columns
        df = df[['name_smell', 'smell']]

        # Group by 'name_smell' and sum the 'smell' column
        report = df.groupby('name_smell').sum()

        # Save the report to a CSV file
        report.to_csv(os.path.join(self.output_path, 'general_overview.csv'))

    def project_report(self):
        """
        Generates a project-specific report, summarizing the smells by project.

        Returns:
        - None
        """
        df = self._load_data()

        # Filter the dataframe to include only the necessary columns
        df = df[['filename', 'name_smell', 'smell']]

        # Extract the project name from the 'filename' column
        df['project_name'] = df['filename'].str.split('\\').str[2]

        # Set the 'smell' column to integer type
        df['smell'] = df['smell'].astype(int)

        # Group by 'project_name' and sum the 'smell' values
        report = df.groupby('project_name').sum()

        # Save the report to a CSV file
        report.to_csv(os.path.join(self.output_path, 'project_overview.csv'))

    def summary_report(self):
        """
        Generates a summary report combining the general smell overview and project-specific details.

        Returns:
        - None
        """
        general_report = self._load_data()[['name_smell', 'smell']].groupby('name_smell').sum()
        project_report = self._load_data()[['filename', 'name_smell', 'smell']]
        project_report['project_name'] = project_report['filename'].str.split('\\').str[2]
        project_report = project_report[['project_name', 'smell']].groupby('project_name').sum()

        # Merge the reports
        with pd.ExcelWriter(os.path.join(self.output_path, 'summary_report.xlsx')) as writer:
            general_report.to_excel(writer, sheet_name='General Overview')
            project_report.to_excel(writer, sheet_name='Project Overview')


    def visualize_smell_report(self):
        """
        Generates a bar chart for the general smell overview report.

        Returns:
        - None
        """
        df = self._load_data()
        df = df[['name_smell', 'smell']]
        report = df.groupby('name_smell').sum()

        # Generate a bar chart
        report.plot(kind='bar', legend=False)
        plt.title('Smell Occurrences by Type')
        plt.xlabel('Smell Type')
        plt.ylabel('Number of Occurrences')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_path, 'smell_report_chart.png'))
        plt.show()

    def cleanup_old_reports(self):
    """
    Cleans up old reports in the output directory.

    Returns:
    - None
    """
    for file in os.listdir(self.output_path):
        if file.endswith('.csv') or file.endswith('.xlsx') or file.endswith('.png'):
            os.remove(os.path.join(self.output_path, file))


    def generate_reports(self):
    """
    Allows the user to choose which reports to generate interactively.

    Returns:
    - None
    """
    print("Select which reports to generate:")
    print("1. General Smell Report")
    print("2. Project-Specific Report")
    print("3. Both Reports")
    print("4. Plot Report")
    print("5. Summary .xlsx Report")
    print("6. Clean-up Old Reports")
    choice = input("Enter your choice: ")
    if choice == '1':
        self.smell_report()
    elif choice == '2':
        self.project_report()
    elif choice == '3':
        self.generate_reports()
    elif choice == '4':
        self.visualize_smell_report()
    elif choice == '5':
        self.summary_report()
    elif choice == '6':
        self.cleanup_old_reports()
    else:
        print("Invalid choice.")
