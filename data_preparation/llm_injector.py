import json
from random import sample
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


class CodeSmellInjector:
    def __init__(
        self, input_file, output_file, smells_file, model_name="gpt2"
    ):
        """
        Initialize the CodeSmellInjector with GPT-2.
        """
        self.input_file = input_file
        self.output_file = output_file
        self.smells_file = smells_file

        # Carica GPT-2
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        # Imposta il pipeline
        self.llm = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            truncation=True,
            max_new_tokens=100,
            device=0,
        )

        # Carica gli smells
        self.CODE_SMELLS = self._load_code_smells()

    def _load_code_smells(self):
        with open(self.smells_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _analyze_code(self, function):
        """
        Analyze the code to determine if a code smell is applicable.
        """
        prompt = (
            f"Analyze the following Python function:\n\n{function['code']}\n\n"
            f"""Decide if one of the following code smells is applicable:
            {', '.join([smell['name'] for smell in self.CODE_SMELLS])}.\n"""
            f"Respond with the name of the applicable code smell or 'no_smell'"
        )
        try:
            response = self.llm(
                prompt, max_new_tokens=20, num_return_sequences=1
            )
            smell = response[0]["generated_text"].strip()
            print(f"AAAAAAAAAAAAAAAAAAAAAAAAAA: {smell}")
            return (
                smell
                if smell in [s["name"] for s in self.CODE_SMELLS]
                else "no_smell"
            )
        except Exception as e:
            print(f"Error during analysis: {e}")
            return "no_smell"

    def _inject_smell(self, function, smell):
        """
        Inject the specified code smell into the function.
        """
        if smell == "no_smell":
            function["injected_code"] = function["code"]
            function["injected_smell"] = "no_smell"
            return function

        prompt = (
            f"Here is the function:\n\n{function['code']}\n\n"
            f"Inject the following code smell: {smell}.\n"
            f"""Ensure the modified code is syntactically valid and add
            the comment '# Injected Smell: {smell}' at the end."""
        )
        try:
            response = self.llm(
                prompt, max_new_tokens=200, num_return_sequences=1
            )
            modified_code = self._extract_modified_code(
                response[0]["generated_text"]
            )
            function["injected_code"] = modified_code
            function["injected_smell"] = smell
            return function
        except Exception as e:
            print(f"Error during injection: {e}")
            function["injected_code"] = function["code"]
            function["injected_smell"] = "error"
            return function

    def _validate_code(self, function):
        """
        Validate the injected code for syntax errors.

        :param function: Function metadata.
        :return: Boolean indicating whether the code is valid.
        """
        try:
            code = function["injected_code"]
            compile(code, "<string>", "exec")  # Validate syntax
            return True
        except SyntaxError:
            print(
                f"Validation failed for function: {function['function_name']}"
            )
            return False

    def inject_code_smells(self):
        """
        Orchestrates the multi-stage pipeline to analyze, inject,
        and validate code smells.
        """
        with open(self.input_file, "r", encoding="utf-8") as f:
            functions = json.load(f)

        results = []
        for function in functions:
            # Stage 1: Analyze
            smell = self._analyze_code(function)

            # Stage 2: Inject
            enriched_function = self._inject_smell(function, smell)

            # Stage 3: Validate
            if self._validate_code(enriched_function):
                results.append(enriched_function)
            else:
                print(
                    f"Skipping invalid function: {function['function_name']}"
                )

        # Save results
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        print(f"Injected code smells saved to {self.output_file}")

    def balance_dataset(self, functions):
        """
        Balance the dataset to ensure equal distribution of functions with
        no smells, with smells, and across different smell types.
        """
        no_smell = [
            f for f in functions if f.get("injected_smell") == "no_smell"
        ]
        smells = [
            f for f in functions if f.get("injected_smell") != "no_smell"
        ]

        smell_types = {smell["name"]: [] for smell in self.CODE_SMELLS}
        for func in smells:
            smell_types[func["injected_smell"]].append(func)

        # Find the minimum count across all categories
        min_count = min(
            len(no_smell),
            min(len(smell_group) for smell_group in smell_types.values()),
        )

        # Balance the dataset by sampling uniformly from each category
        balanced_functions = sample(no_smell, min_count) + [
            sample(smell_group, 1)[0]
            for smell_group in smell_types.values()
            for _ in range(min_count)
        ]
        return balanced_functions


def main():
    input_file = "datasets/functions_extracted.json"
    output_file = "datasets/functions_with_smells.json"
    smells_file = "data_preparation/smells_file.json"

    injector = CodeSmellInjector(
        input_file=input_file, output_file=output_file, smells_file=smells_file
    )

    print("Starting code smell injection...")
    injector.inject_code_smells()

    with open(output_file, "r", encoding="utf-8") as f:
        injected_functions = json.load(f)

    print(
        f"""{len(injected_functions)} functions processed
          with injected code smells."""
    )
    for i, function in enumerate(injected_functions[:5]):
        print(f"Function {i+1}: {function['function_name']}")
        print(f"Injected Smell: {function.get('injected_smell', 'None')}")
        print(f"Modified Code:\n{function['injected_code']}\n")


if __name__ == "__main__":
    main()
