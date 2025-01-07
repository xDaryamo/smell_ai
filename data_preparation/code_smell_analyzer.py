import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from components.inspector import Inspector


class CodeSmellAnalyzer:
    """
    Class to analyze code smells in functions extracted from a dataset.
    This class uses the Inspector class to detect code smells in
    individual functions.
    """

    def __init__(
        self, dataset_path, output_dir, max_workers=4, log_interval=100
    ):
        """
        Initialize the analyzer with the dataset path and output directory.

        Args:
            dataset_path (str): Path to the dataset JSON file.
            output_dir (str): Directory to save results.
            max_workers (int): Maximum number of threads for parallelization.
            log_interval (int): Number of functions to process before logging progress.
        """
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.log_interval = log_interval

        os.makedirs(output_dir, exist_ok=True)
        self.inspector = Inspector(output_path=output_dir)
        self.clean_functions = []
        self.smelly_functions = []
        self.file_cache = {}  # Cache to store inspection results for files

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(output_dir, "analysis.log")),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def load_dataset(self):
        """Load the dataset from the JSON file."""
        with open(self.dataset_path, "r") as f:
            self.dataset = json.load(f)

    def analyze_function_in_file(self, function_data):
        """
        Analyze a function by analyzing the entire file and filtering results.

        Args:
            function_data (dict): Function data containing file_path,
            start_line, end_line, etc.

        Returns:
            dict: Result indicating if the function is smelly and its smells.
        """
        file_path = function_data["file_path"]

        # Use cache if the file has already been inspected
        if file_path not in self.file_cache:
            try:
                self.file_cache[file_path] = self.inspector.inspect(file_path)
            except Exception as e:
                self.logger.error(f"Error analyzing file {file_path}: {e}")
                return {
                    "function_data": function_data,
                    "smelly": False,
                    "smells": [],
                }

        results = self.file_cache[file_path]
        function_smells = results[
            (results["function_name"] == function_data["function_name"])
            & (results["line"] >= function_data["start_line"])
            & (results["line"] <= function_data["end_line"])
        ]

        if not function_smells.empty:
            return {
                "function_data": function_data,
                "smelly": True,
                "smells": function_smells.to_dict(orient="records"),
            }
        else:
            return {
                "function_data": function_data,
                "smelly": False,
                "smells": [],
            }

    def analyze_dataset_parallel(self):
        """
        Analyze the entire dataset of functions in parallel.

        Returns:
            tuple: Lists of clean and smelly functions.
        """
        self.load_dataset()

        clean_functions = []
        smelly_functions = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_function = {
                executor.submit(
                    self.analyze_function_in_file, function_data
                ): function_data
                for function_data in self.dataset
            }

            for i, future in enumerate(
                as_completed(future_to_function), start=1
            ):
                function_data = future_to_function[future]
                try:
                    result = future.result()
                    if result["smelly"]:
                        smelly_functions.append(result)
                    else:
                        clean_functions.append(function_data)
                except Exception as e:
                    self.logger.error(
                        f"Error analyzing function "
                        f"{function_data['function_name']} "
                        f"in file {function_data['file_path']}: {e}"
                    )

                # Log progress every `log_interval` functions
                if i % self.log_interval == 0 or i == len(self.dataset):
                    self.logger.info(
                        f"Processed {i}/{len(self.dataset)} functions..."
                    )

        return clean_functions, smelly_functions

    def save_results(self, clean_functions, smelly_functions):
        """Save clean and smelly functions to JSON files."""
        clean_path = os.path.join(self.output_dir, "clean_functions.json")
        smelly_path = os.path.join(self.output_dir, "smelly_functions.json")

        with open(clean_path, "w") as f:
            json.dump(clean_functions, f, indent=4)

        with open(smelly_path, "w") as f:
            json.dump(smelly_functions, f, indent=4)

        self.logger.info(f"Results saved: {clean_path}, {smelly_path}")

    def run(self):
        """Run the analysis process."""
        self.logger.info("Starting dataset analysis...")
        clean_functions, smelly_functions = self.analyze_dataset_parallel()
        self.save_results(clean_functions, smelly_functions)
        self.logger.info(
            f"Analysis completed. Clean functions: {len(clean_functions)}, "
            f"Smelly functions: {len(smelly_functions)}"
        )


if __name__ == "__main__":
    # Define paths for the dataset and output
    dataset_path = "datasets/partial_dataset.json"
    output_dir = "datasets/output_analysis"

    # Initialize and run the analyzer
    analyzer = CodeSmellAnalyzer(dataset_path, output_dir, max_workers=16)
    analyzer.run()
