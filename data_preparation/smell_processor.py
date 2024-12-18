# SmellProcessor: Coordinates applying smells to functions
from data_preparation.smell_model import SmellModel


class SmellProcessor:
    def __init__(self, model: SmellModel, smell_descriptions: dict[str, str]):
        self.model = model
        self.smell_descriptions = smell_descriptions

    def process_functions(self, functions: list[dict]) -> list[dict]:
        """
        Process a list of functions to inject smells where applicable.
        """
        results = []
        for func in functions:
            file_path = func.get("file_path")
            function_name = func.get("function_name")
            libraries_used = func.get("libraries_used")
            code = func.get("code")
            smells_to_check = func.get(
                "smells_to_check", list(self.smell_descriptions.keys())
            )

            for smell in smells_to_check:
                print(
                    f"""Checking applicability of '{smell}'
                     for function '{function_name}'..."""
                )
                description = self.smell_descriptions[smell]

                # Check applicability in batches
                applicable = self.model.check_smell_applicability(
                    [code], smell, description
                )[0]
                if applicable:
                    print(f"""Injecting '{smell}'
                          into function '{function_name}'...""")

                    # Inject smell in batches
                    dirty_code = self.model.generate_smelly_code(
                        [code], smell, description
                    )[0]
                    results.append(
                        {
                            "file_path": file_path,
                            "function_name": function_name,
                            "libraries_used": libraries_used,
                            "original_code": code,
                            "applied_smell": smell,
                            "dirty_code": dirty_code,
                        }
                    )
                else:
                    print(
                        f"""Smell '{smell}' is not applicable
                        to function '{function_name}'."""
                    )

        return results
