import argparse
import json
from pathlib import Path
from data_preparation.directory_processor import DirectoryProcessor


class DatasetBuilder:
    """
    A class to coordinate the extraction and saving of
    functions to a structured dataset.
    """

    def __init__(self, input_directory, output_file):
        """
        Initializes the FunctionDatasetBuilder.
        Args:
            input_directory (str): Directory containing Python files.
            output_file (str): Path to the output JSON file.
        """
        self.input_directory = input_directory
        self.output_file = output_file

    def build_dataset(self):
        """
        Extracts functions and saves them to a JSON file.
        """
        # Process the directory
        processor = DirectoryProcessor(self.input_directory)
        processor.process_files()
        all_functions = processor.get_all_functions()

        # Save the results to JSON
        self._save_to_json(all_functions)
        print(
            f"Extracted {len(all_functions)} functions to {self.output_file}"
        )

    def _save_to_json(self, data):
        """
        Saves extracted functions to a JSON file.
        Args:
            data (list): List of function dictionaries.
        """
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving to {self.output_file}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Extract functions from Python files
        and save them to JSON."""
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to the input directory containing Python files.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="""Path to the output directory where the functions_clean.json
        file will be saved.""",
    )

    args = parser.parse_args()

    input_directory = Path(args.input_dir).resolve()
    output_directory = Path(args.output_dir).resolve()

    if not input_directory.exists() or not input_directory.is_dir():
        raise FileNotFoundError(
            f"Input directory '{input_directory}' is not a valid directory."
        )

    if not output_directory.exists():
        print(
                "Output directory does not exist, creating it..."
            )
        output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / "functions_clean.json"

    print(f"Input Directory: {input_directory}")
    print(f"Output File: {output_file}")

    builder = DatasetBuilder(str(input_directory), str(output_file))
    builder.build_dataset()
