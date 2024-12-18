# DataManager: Handles loading and saving JSON files
import json
from pathlib import Path


class DataManager:
    @staticmethod
    def load_json(file_path: str) -> list[dict]:
        """
        Load clean functions from a JSON file.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file {file_path} does not exist.")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json(data: list[dict], file_path: str):
        """
        Save the results to a JSON file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Injected functions saved to: {file_path}")
