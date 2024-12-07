import os
import pandas as pd


class FileUtils:
    """Handles file and directory-related operations."""

    @staticmethod
    def merge_results(input_dir: str, output_dir: str) -> None:
        """
        Merges analysis results from multiple projects into a single CSV.

        Parameters:
        - input_dir (str): Directory containing analysis results.
        - output_dir (str): Directory where the merged results will be saved.
        """
        dataframes = []
        for subdir, _, files in os.walk(input_dir):
            if "to_save.csv" in files:
                df = pd.read_csv(os.path.join(subdir, "to_save.csv"))
                if len(df) > 0:
                    dataframes.append(df)

        if dataframes:
            combined_df = pd.concat(dataframes)
            combined_df = combined_df[combined_df["filename"] != "filename"]
            combined_df = combined_df.reset_index()

            os.makedirs(output_dir, exist_ok=True)
            combined_df.to_csv(
                os.path.join(output_dir, "overview_output.csv"), index=False
            )
        else:
            print("No valid results found for merging.")

    @staticmethod
    def clean_directory(output_path: str) -> None:
        """
        Cleans the specified output directory.

        Parameters:
        - output_path (str): Path to the directory to be cleaned.
        """
        if os.path.exists(output_path):
            if os.name == "nt":
                os.system(f"rmdir /s /q {output_path}")
            else:
                os.system(f"rm -r {output_path}")

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
