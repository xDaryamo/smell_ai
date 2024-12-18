# SmellModel: Encapsulates LLM interactions
import torch
from transformers import pipeline


class SmellModel:
    def __init__(self, model_name="codellama/CodeLlama-7b-hf"):
        """
        Initialize the smell model with a specified LLM.
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = pipeline(
            "text-generation", model=self.model_name, device=self.device
        )

    def check_smell_applicability(
        self, functions: list[str], smell: str, smell_description: str
    ) -> list[bool]:
        """
        Batch check if a particular smell is applicable to a list of functions.
        """
        prompts = [
            (
                f"Analyze the following Python function:\n"
                f"{function_code}\n\n"
                f"""Does the function exhibit
                characteristics where the '{smell}' """
                f"smell could apply? Respond with 'Yes' or 'No'.\n\n"
                f"Description of the smell:\n{smell_description}"
            )
            for function_code in functions
        ]

        responses = self.pipeline(
            prompts, max_length=50, num_return_sequences=1, batch_size=8
        )
        return [
            "yes" in response[0]["generated_text"].strip().lower()
            for response in responses
        ]

    def generate_smelly_code(
        self, functions: list[str], smell: str, smell_description: str
    ) -> list[str]:
        """
        Batch generate smelly code for a list of functions.
        """
        prompts = [
            (
                f"Given the following clean Python function:\n"
                f"{function_code}\n\n"
                f"Inject the '{smell}' code smell into the function.\n"
                f"Description of the smell:\n{smell_description}"
            )
            for function_code in functions
        ]

        responses = self.pipeline(
            prompts, max_length=300, num_return_sequences=1, batch_size=8
        )
        return [response[0]["generated_text"] for response in responses]
