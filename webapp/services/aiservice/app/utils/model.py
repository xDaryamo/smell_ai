import os
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)


class Model:
    """
    Class for loading and using the fine-tuned
    AI model for code smell detection.
    """

    def __init__(self):
        self.tokenizer = None
        self.model = None

    def load_fine_tuned_model(
        self, model_dir: str = "../model_training_and_evaluation/qwen"
    ):
        """
        Load the fine-tuned model and tokenizer from a directory.
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError("Model directory does not exist.")

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype="auto",
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
        )
        print(f"Fine-tuned model successfully loaded from {model_dir}.")

    def detect_code_smell(
        self, code_snippet: str,
        max_new_tokens: int = 512,
        temperature: float = 0.6
    ) -> dict:
        """
        Detect code smells using the AI model with Chain-of-Thought reasoning.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        try:
            # Define the Chain-of-Thought prompt
            messages = [
                {
                    "role": "system",
                    "content":
                    """You are Qwen, a helpful coding assistant trained
                    to analyze and refactor Python code. """
                    """Analyze the provided code step-by-step
                    to identify code smells.""",
                },
                {
                    "role": "user",
                    "content": f"Code:\n{code_snippet}\n\nQuestion:\n"
                    """What is wrong with this code? Please explain
                    step-by-step before providing a label.""",
                },
            ]

            # Create prompt text
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            # Tokenize inputs
            model_inputs = self.tokenizer([text], return_tensors="pt").to(
                self.model.device
            )

            # Generate predictions
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                repetition_penalty=1.0,
            )

            # Decode the response
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(
                    model_inputs.input_ids,
                    generated_ids
                )
            ]
            response = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]

            return {
                "success": True,
                "analysis": response,
                "label": "Code Smell Detected",
            }

        except Exception as e:
            return {"success": False, "message": str(e)}
