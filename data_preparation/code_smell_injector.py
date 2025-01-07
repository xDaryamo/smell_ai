import random
from data_preparation.base_llm import BaseLLM


class CodeSmellInjector:
    """
    A class to inject code smells into clean Python
    functions using a language model (LLM).
    """

    def __init__(self, llm_model: BaseLLM, max_smells=2):
        """
        Initializes the CodeSmellInjector.

        Args:
            llm_model (BaseLLM): An instance of a language
            model used for code generation.
            max_smells (int): Maximum number of code smells to
            inject per function (default is 2).
        """
        self.llm_model = llm_model  # Instance of a language model
        self.max_smells = max_smells

        # Equal distribution of code smells with descriptions and examples
        self.smell_descriptions = {
            "Broadcasting Feature Not Used": {
                "description": (
                    "This smell occurs when a developer uses explicit "
                    "tiling or tensor operations without "
                    "leveraging broadcasting, a feature that "
                    "efficiently manipulates tensors."
                ),
                "example": "tensor_a = tf.tile(tensor_b, [1, 3]) + "
                "tensor_c  # Should use broadcasting",
                "definition": "Using tensors without utilizing "
                "broadcasting operations.",
                "static_analysis_rule": (
                    "Verify TensorFlow imports and tensor operations. "
                    "Check if tiling is used "
                    "when broadcasting could achieve the same result."
                ),
                "rationale": (
                    "Broadcasting reduces memory usage and improves "
                    "code readability by avoiding explicit tiling."
                ),
            },
            "Chain Indexing": {
                "description": (
                    "This smell involves using chained indexing on "
                    "Pandas DataFrames, which can lead to performance "
                    "issues and unpredictable behavior."
                ),
                "example": 'value = df["column"]["subcolumn"] '
                "# Should use loc or iloc instead",
                "definition": "Accessing DataFrame "
                "elements with chained indexing.",
                "static_analysis_rule": (
                    "Detect consecutive square brackets ([][]) in "
                    "Pandas functions to identify chained indexing."
                ),
                "rationale": (
                    "Chained indexing can cause unintended behavior "
                    "due to intermediate copies of data being created."
                ),
            },
            "Columns and DataType Not Explicitly Set": {
                "description": (
                    "This smell occurs when DataFrame columns "
                    "their data types are not"
                    "explicitly defined, which can lead to "
                    "unexpected type inference."
                ),
                "example": "df = pd.DataFrame(data) "
                " # Columns and types should be specified",
                "definition": (
                    "Creating DataFrames without declaring "
                    "column names and data types "
                    "explicitly."
                ),
                "static_analysis_rule": (
                    "Check if Pandas DataFrame instantiations "
                    "or CSV reads explicitly "
                    "set columns and types."
                ),
                "rationale": (
                    "Explicitly setting columns and types "
                    "ensures consistency and avoids "
                    "runtime errors."
                ),
            },
            "Dataframe Conversion API Misused": {
                "description": (
                    "This smell refers to using .values instead of "
                    ".to_numpy() for converting a Pandas DataFrame "
                    "to a NumPy array."
                ),
                "example": "array = df.values  # Use df.to_numpy() instead",
                "definition": (
                    "Converting DataFrames to NumPy arrays using "
                    ".values instead of .to_numpy()."
                ),
                "static_analysis_rule": (
                    "Identify calls to .values on "
                    "DataFrame objects in the code."
                ),
                "rationale": (
                    "Using .to_numpy() is the recommended approach "
                    "for future compatibility and clarity."
                ),
            },
            "Deterministic Algorithm Option Not Used": {
                "description": (
                    "This smell occurs when deterministic algorithm "
                    "options are not enabled in machine learning "
                    "pipelines, causing non-reproducible results."
                ),
                "example": "torch.backends.cudnn.deterministic = True "
                "# Ensure deterministic behavior",
                "definition": (
                    "Not enabling deterministic "
                    "algorithm options in ML pipelines."
                ),
                "static_analysis_rule": (
                    "Verify that torch.use_deterministic_algorithms(True) "
                    "is used in PyTorch code."
                ),
                "rationale": (
                    "Enabling deterministic algorithms ensures "
                    "reproducibility, crucial for debugging "
                    "and model validation."
                ),
            },
            "In-Place APIs Misused": {
                "description": (
                    "This smell involves assuming in-place changes "
                    "to Pandas DataFrames without explicitly assigning "
                    "the result to a variable."
                ),
                "example": 'df.drop("column", inplace=True) '
                "# Ensure result is assigned if needed",
                "definition": (
                    "Misusing in-place APIs by not correctly "
                    "managing their results."
                ),
                "static_analysis_rule": (
                    "Identify Pandas API calls and verify "
                    "proper result handling."
                ),
                "rationale": (
                    "Explicit result handling avoids unintended "
                    "data loss and improves code clarity."
                ),
            },
            "Empty Column Misinitialization": {
                "description": (
                    "This smell occurs when new DataFrame columns "
                    "are initialized with empty strings or zeros, "
                    "which can lead to inconsistencies."
                ),
                "example": 'df["new_column"] = ""  # Avoid using '
                "empty strings for initialization",
                "definition": (
                    "Initializing columns with empty strings "
                    "or zeros instead of appropriate default values."
                ),
                "static_analysis_rule": (
                    "Detect new column assignments with empty "
                    "strings or zero values."
                ),
                "rationale": (
                    "Proper initialization avoids potential "
                    "issues with downstream data processing."
                ),
            },
            "Gradients Not Cleared Before Backward Propagation": {
                "description": (
                    "This smell occurs when gradients are not "
                    "cleared before backward propagation in PyTorch, "
                    "leading to incorrect updates."
                ),
                "example": "loss.backward(); optimizer.step() "
                "# Add optimizer.zero_grad() before backward",
                "definition": (
                    "Failing to clear gradients before "
                    "backward propagation in PyTorch."
                ),
                "static_analysis_rule": (
                    "Check for optimizer.zero_grad() "
                    "before backward propagation calls."
                ),
                "rationale": (
                    "Clearing gradients ensures accurate "
                    "updates and prevents gradient accumulation."
                ),
            },
            "Memory Not Freed": {
                "description": (
                    "This smell refers to declaring machine learning "
                    "models in loop operations without explicitly "
                    "releasing memory at the end of each iteration."
                ),
                "example": (
                    "for data in dataset:\n"
                    "    model = train_model(data)\n"
                    "    del model  # Use library-specific memory "
                    "management methods"
                ),
                "definition": (
                    "Not using ad-hoc functions to free memory "
                    "in loop operations involving ML models."
                ),
                "static_analysis_rule": (
                    "Identify ML model declarations in loops and "
                    "verify memory-free function calls."
                ),
                "rationale": (
                    "Freeing memory avoids memory leaks and ensures "
                    "efficient resource usage during iterative processes."
                ),
            },
            "Merge API Parameter Not Explicitly Set": {
                "description": (
                    "This smell occurs when the 'how' and 'on' parameters "
                    "are not explicitly specified during a Pandas "
                    "merge operation."
                ),
                "example": "df_merged = df1.merge(df2) "
                "# Specify 'how' and 'on' parameters",
                "definition": (
                    "Not explicitly setting the 'how' and "
                    "'on' parameters in Pandas merge operations."
                ),
                "static_analysis_rule": (
                    "Identify merge operations and check if 'how' "
                    "and 'on' parameters are specified."
                ),
                "rationale": (
                    "Explicitly setting these parameters ensures "
                    "clarity and avoids unexpected merge behavior."
                ),
            },
            "NaN Equivalence Comparison Misused": {
                "description": (
                    "This smell involves using 'np.nan' for equivalence "
                    "comparison, which is not valid as NaN values "
                    "are not equal to themselves."
                ),
                "example": "if value == np.nan: "
                "# Use np.isnan(value) instead",
                "definition": (
                    "Comparing values to 'np.nan' instead of "
                    "using the correct method."
                ),
                "static_analysis_rule": (
                    "Check for equivalence comparisons "
                    "involving 'np.nan' in the code."
                ),
                "rationale": (
                    "Proper handling of NaN ensures code "
                    "correctness and avoids logical errors."
                ),
            },
            "TensorArray Not Used": {
                "description": (
                    "This smell occurs when 'tf.constant()' is "
                    "used to initialize a tensor array inside a loop, instead "
                    "of using 'tf.TensorArray()', which "
                    "is designed for this purpose."
                ),
                "example": (
                    "for i in range(n):\n"
                    "    tensor = tf.constant([1, 2, 3]) "
                    " # Use tf.TensorArray instead"
                ),
                "definition": (
                    "Initializing tensor arrays with 'tf.constant()' "
                    "inside loops without using 'tf.TensorArray()'."
                ),
                "static_analysis_rule": (
                    "Identify loops initializing tensors with 'tf.constant()' "
                    "and verify the use of 'tf.TensorArray()'."
                ),
                "rationale": (
                    "Using 'tf.TensorArray()' ensures memory efficiency "
                    "and prevents runtime errors in loops."
                ),
            },
            "Randomness Uncontrolled": {
                "description": (
                    "This smell occurs when randomness is not "
                    "controlled by setting a seed value, "
                    "leading to non-reproducible results in "
                    "experiments or models."
                ),
                "example": (
                    "import random\n"
                    "random.shuffle(data)  # Add random.seed(42) "
                    "before shuffling for reproducibility"
                ),
                "definition": (
                    "Not setting a fixed seed for random number "
                    "generators in libraries like random, numpy, or PyTorch."
                ),
                "static_analysis_rule": (
                    "Detect usage of random operations "
                    "(e.g., random.shuffle, np.random, torch.rand) "
                    "and verify if a seed is set beforehand."
                ),
                "rationale": (
                    "Controlling randomness is crucial for reproducibility "
                    "in ML experiments, debugging, and validation."
                ),
            },
            "Hyperparameter Not Explicitly Set": {
                "description": (
                    "This smell occurs when a developer does not explicitly "
                    "set the hyperparameter of an ML algorithm."
                ),
                "example": "model = Model(alpha=None) "
                "# Explicitly set alpha for reproducibility",
                "definition": "Not explicitly setting the "
                "hyperparameters of a machine learning algorithm.",
                "static_analysis_rule": (
                    "The variability in the naming conventions and "
                    "configurations of hyperparameters across different "
                    "machine learning algorithms "
                    "and libraries limits the detection through a rule-based "
                    "approach. This variability makes it challenging "
                    "for static analysis "
                    "to accurately identify instances of missing or "
                    "incorrectly set hyperparameters, as it would require "
                    "a comprehensive understanding "
                    "of the specific hyperparameter requirements for each "
                    "algorithm and library combination."
                ),
                "rationale": (
                    "Explicitly setting hyperparameters ensures "
                    "reproducibility, clarity, and a structured "
                    "approach to model tuning."
                ),
            },
            "Matrix Multiplication API Misused": {
                "description": (
                    "This smell refers to when the developer uses "
                    "the function 'np.dot' to multiply a Numpy matrix."
                ),
                "example": "result = np.dot(matrix_a, matrix_b) "
                "# Should use '@' operator or np.matmul",
                "definition": "Using 'np.dot' for matrix "
                "multiplication instead of modern alternatives.",
                "static_analysis_rule": (
                    "When the codebase includes the NumPy library and "
                    "the method np.dot() is used to multiply matrices."
                ),
                "rationale": (
                    "CodeSmile will scan through the provided codebase, "
                    "specifically targeting functions related to "
                    "matrix multiplication. "
                    "It ensures that the NumPy library is imported and "
                    "identifies instances where the np.dot function is used. "
                    "A smell instance is logged if the function is used for "
                    "matrix multiplication."
                ),
            },
            "Pytorch Call Method Misused": {
                "description": (
                    "This smell regards when a developer uses the function "
                    "'self.net.forward()' to forward the input to the network."
                ),
                "example": "output = self.net.forward(input) "
                "# Use self.net(input) instead",
                "definition": "Calling 'self.net.forward()' directly "
                "instead of using the model instance as a callable.",
                "static_analysis_rule": (
                    "Detect the usage of the forward method within the "
                    "context of a PyTorch neural network, specifically "
                    "by calling self.net.forward()."
                ),
                "rationale": (
                    "Proper usage of PyTorch models improves code "
                    "readability and maintains consistency with "
                    "best practices."
                ),
            },
            "Unnecessary Iteration": {
                "description": (
                    "This smell is regarded when a developer uses a "
                    "loop operation rather than the corresponding "
                    "Pandas function."
                ),
                "example": (
                    "for index, row in df.iterrows():\n    "
                    "df.loc[index, 'new_col'] = row['existing_col'] "
                    "* 2  # Use df['new_col'] = df['existing_col'] * 2"
                ),
                "definition": "Using loops instead of Pandas' "
                "vectorized operations.",
                "static_analysis_rule": (
                    "Dynamic analysis is needed as static analysis "
                    "cannot ensure the proposed solution replicates "
                    "the loop's functionality."
                ),
                "rationale": (
                    "Replacing loops with vectorized operations "
                    "improves performance and reduces code complexity."
                ),
            },
        }

    def inject_smells(self, clean_function, num_smells=None):
        """
        Injects code smells into a clean Python function.

        Args:
            clean_function (str): The source code of the "
            "clean function as a string.
            num_smells (int, optional): Maximum number of "
            "code smells to inject. Defaults to `self.max_smells`.

        Returns:
            str: The source code of the function with injected code smells.
        """
        if num_smells is None:
            num_smells = self.max_smells

        # Select smells randomly, up to the maximum allowed
        selected_smells = self._select_smells(random.randint(1, num_smells))

        # Build the prompt dynamically
        prompt = self._build_prompt(clean_function, selected_smells)

        # Call the LLM to generate the smelly function
        response = self.llm_model.generate_response(prompt)

        if response.startswith("```python") and response.endswith("```"):
            response = response[9:-3].strip()

        return response, selected_smells

    def _select_smells(self, num_smells):
        """
        Selects a set of code smells based on equal distribution.

        Args:
            num_smells (int): Number of code smells to select.

        Returns:
            list: A list of selected code smell names.
        """
        smells = list(self.smell_descriptions.keys())

        # Randomly select smells with equal probability
        return random.sample(smells, k=num_smells)

    def _build_prompt(self, clean_function, selected_smells):
        """
        Builds the prompt to instruct the LLM to inject code smells.

        Args:
            clean_function (str): The source code of the clean function.
            selected_smells (list): The selected code smells to inject.

        Returns:
            str: The prompt to send to the LLM.
        """
        # Construct details of the smells to inject
        smells_details = "\n\n".join(
            [
                f"- {smell}:\n"
                f"  Description: "
                f"{self.smell_descriptions[smell]['description']}\n"
                f"  Example: "
                f"{self.smell_descriptions[smell]['example']}\n"
                f"  Definition: "
                f"{self.smell_descriptions[smell]['definition']}\n"
                f"  Static Analysis Rule: "
                f"{self.smell_descriptions[smell]['static_analysis_rule']}\n"
                f"  Rationale: {self.smell_descriptions[smell]['rationale']}"
                for smell in selected_smells
            ]
        )

        # Construct the prompt
        prompt = (
            "You are a code generation assistant specializing in introducing "
            'intentional flaws ("code smells") into Python code. '
            "Below is a clean Python method:\n\n"
            f"{clean_function}\n\n"
            "Task:\n"
            "1. Modify the function above to introduce the "
            "following code smells:\n"
            f"{smells_details}\n\n"
            "2. Ensure the function remains functional but "
            "reflects the specified flaws.\n"
            "3. Do not create any new methods or functions. "
            "All modifications must be "
            "made within the given function.\n"
            "4. Do not add any imports or modify the import statements.\n"
            "5. Return only the modified function code.\n"
            "Instructions:\n"
            "- Inject the specified code smells directly into the function.\n"
            "- Ensure all modifications are realistic examples "
            "of the specified code smells.\n"
            "- Do not include any additional comments, explanations, "
            "or external dependencies.\n"
        )

        return prompt
