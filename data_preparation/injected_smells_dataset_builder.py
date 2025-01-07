import json
import logging
import os
from data_preparation.code_smell_injector import CodeSmellInjector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class InjectedSmellsDatasetBuilder:
    def __init__(
        self,
        injector: CodeSmellInjector,
        checkpoint_path="checkpoint.json",
        output_path="smelly_functions.json",
        input_path="data/clean_functions.json",
    ):
        """
        Initializes the InjectedSmellsDatasetBuilder.

        Args:
            injector (CodeSmellInjector): An instance of CodeSmellInjector.
            checkpoint_path (str): Path to the checkpoint file.
            output_path (str): Path to the incremental output JSON file.
            input_path (str): Path to the input JSON file containing functions to process.
        """
        self.injector = injector
        self.checkpoint_path = checkpoint_path
        self.output_path = output_path
        self.input_path = input_path

    def load_checkpoint(self):
        """Loads the checkpoint and previously processed data if they exist."""
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                try:
                    checkpoint = json.load(f)
                except json.JSONDecodeError:
                    logging.warning(
                        f"Checkpoint file {self.checkpoint_path} is empty or corrupted. Resetting checkpoint."
                    )
                    checkpoint = {"processed": []}
        else:
            checkpoint = {"processed": []}

        if os.path.exists(self.output_path):
            with open(self.output_path, "r", encoding="utf-8") as f:
                try:
                    smelly_functions = json.load(f)
                except json.JSONDecodeError:
                    logging.warning(
                        f"Output file {self.output_path} is empty or corrupted. Starting fresh."
                    )
                    smelly_functions = []
        else:
            smelly_functions = []

        return checkpoint, smelly_functions

    def save_checkpoint(self, processed_indices):
        """Saves the checkpoint to a file."""
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"processed": processed_indices}, f, indent=4)

    def save_incremental_output(self, smelly_functions):
        """Saves the incrementally updated output to the output file."""
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(smelly_functions, f, indent=4)

    def process_dataset(self):
        """
        Processes the dataset by injecting code smells and saving the results incrementally.
        """
        with open(self.input_path, "r", encoding="utf-8") as f:
            functions = json.load(f)

        total_functions = len(functions)
        logging.info(
            f"Starting processing {total_functions} functions from {self.input_path}"
        )

        # Load checkpoint and previously saved output
        checkpoint, smelly_functions = self.load_checkpoint()
        processed_indices = set(checkpoint["processed"])

        for index, func in enumerate(functions):
            if index in processed_indices:
                logging.info(
                    f"Skipping function {index + 1}/{total_functions}, already processed."
                )
                continue

            # Extract only the function code
            clean_code = func["code"]

            # Inject smells into the clean function
            smelly_function, smells = self.injector.inject_smells(clean_code)

            # Remove Python code block markers if present
            if smelly_function.startswith(
                "```python"
            ) and smelly_function.endswith("```"):
                smelly_function = smelly_function[9:-3].strip()

            # Prepare the result structure
            smelly_functions.append(
                {
                    "code": smelly_function,
                    "labels": smells,
                }
            )

            # Log progress
            logging.info(
                f"Processed function {index + 1}/{total_functions}: Labels = {smells}"
            )

            # Update checkpoint and save incremental output
            processed_indices.add(index)
            self.save_checkpoint(list(processed_indices))
            self.save_incremental_output(smelly_functions)

        logging.info(
            f"Processing complete. Full dataset saved to {self.output_path}"
        )


if __name__ == "__main__":
    from data_preparation.qwen_llm import QwenLLM

    # Initialize the LLM model
    llm_model = QwenLLM()

    # Initialize the CodeSmellInjector
    injector = CodeSmellInjector(llm_model, max_smells=3)

    checkpoint_path = "datasets/output_analysis/checkpoint.json"
    input_path = "datasets/output_analysis/clean_functions.json"
    output_path = "datasets/output_analysis/injected.json"

    # Initialize the InjectedSmellsDatasetBuilder
    dataset_builder = InjectedSmellsDatasetBuilder(
        injector, checkpoint_path, output_path, input_path
    )

    dataset_builder.process_dataset()
