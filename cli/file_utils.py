import os
import shutil
import pandas as pd


class FileUtils:
    """Handles file and directory-related operations."""

    @staticmethod
    def merge_results(input_dir: str, output_dir: str) -> None:
        """
        Merges analysis results from multiple projects into a single CSV.

        Parameters:
        - input_dir (str): Directory containing analysis results
          (project_name.csv files).
        - output_dir (str): Directory where the merged results will be saved.
        """
        dataframes = []
        print(f"Looking for CSV files in directory: {input_dir}")

        # Check the input_dir itself for CSV files (not just subdirectories)
        for subdir, _, files in os.walk(input_dir):
            print(f"Checking directory: {subdir}")
            for file in files:
                if file.endswith(".csv"):  # Look for all CSV files
                    file_path = os.path.join(subdir, file)
                    print(f"Found CSV file: {file_path}")

                    df = pd.read_csv(file_path)
                    if len(df) > 0:
                        dataframes.append(df)
                    else:
                        print(f"Skipping empty CSV: {file_path}")

        # If we have CSV files, merge them
        if dataframes:
            print("Merging dataframes...")
            combined_df = pd.concat(
                dataframes, ignore_index=True
            )  # Concatenate all dataframes
            combined_df = combined_df[
                combined_df["filename"] != "filename"
            ]  # Clean invalid rows
            combined_df = combined_df.reset_index(drop=True)

            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Save the merged results to a CSV file
            combined_df.to_csv(os.path.join(output_dir, "overview.csv"), index=False)
            print(
                "Results successfully merged" f"and saved to {output_dir}/overview.csv"
            )
        else:
            print("No Smells Detected. No CSV files found or they were empty.")

    @staticmethod
    def clean_directory(root_path: str, subfolder_name: str = "output") -> str:
        """
        Cleans or creates a specified subfolder within a root directory.

        Parameters:
        - root_path (str): Root directory where the subfolder will be created.
        - subfolder_name (str): Name of the subfolder to clean or create.

        Returns:
        - str: Path to the cleaned or created subfolder.
        """
        output_path = os.path.join(root_path, subfolder_name)

        if os.path.exists(output_path):
            # Remove only the contents of the 'output' folder
            for filename in os.listdir(output_path):
                file_path = os.path.join(output_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove file or symlink
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove directory
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            try:
                # Create the 'output' folder if it doesn't exist
                os.makedirs(output_path)
            except OSError as e:
                print(f"Error: Could not create output folder: {output_path}")
                raise SystemExit from e

        return output_path

    @staticmethod
    def get_python_files(path: str) -> list[str]:
        """
        Retrieves all Python files from the specified path.

        Parameters:
        - path (str): Path to search for Python files.

        Returns:
        - list[str]: List of Python file paths.
        """
        result = []
        if os.path.isfile(path) and path.endswith(".py"):
            return [path]

        for root, dirs, files in os.walk(path):
            if "venv" in dirs:
                dirs.remove("venv")
            if "lib" in dirs:
                dirs.remove("lib")
            for file in files:
                if file.endswith(".py"):
                    result.append(os.path.abspath(os.path.join(root, file)))
        return result
