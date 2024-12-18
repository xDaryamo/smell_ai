import argparse
from pathlib import Path
from data_preparation.data_manager import DataManager
from data_preparation.smell_model import SmellModel
from data_preparation.smell_processor import SmellProcessor


class SmellInjector:
    def __init__(self, input_dir, output_file,
                 model_name="codellama/CodeLlama-7b-hf"):
        self.input_dir = input_dir
        self.output_file = output_file
        self.model = SmellModel(model_name=model_name)
        self.processor = SmellProcessor(self.model, self.smell_descriptions)
        self.smell_descriptions = {
            "Chain Indexing": (
                """Modify the code to use chained indexing when accessing
                Pandas DataFrame elements. Chained indexing occurs when
                you access a DataFrame using consecutive indexing operations,
                like `df['column'][index]`. While valid, this approach can
                cause performance issues and unexpected behavior
                due to ambiguity in how Pandas processes it.\n\n"
                Example of clean code:\n"
                    df.loc[index, 'column']\n\n"
                Inject the smell:\n"
                    df['column'][index]"""
            ),
            "DataFrame_Conversion_API_Misused": (
                """Modify the code to use the deprecated `values` attribute
                of a Pandas DataFrame for data conversion.
                Using `.values` is discouraged because
                it has an unclear return type and can lead to issues
                when working with data. Instead, use explicit methods
                such as `.to_numpy()` for conversion.\n\n
                Example of clean code:\n
                    array = df.to_numpy()\n\n
                Inject the smell:\n
                    array = df.values"""
            ),
            "Gradients_Not_Cleared_Before_Backward_Propagation": (
                """Modify the code so that gradients are not cleared before
                backward propagation in a PyTorch training loop.
                Failing to call `optimizer.zero_grad()` before
                calling `backward()` leads to unintended gradient accumulation,
                which can result in incorrect training behavior.\n\n
                Example of clean code:\n
                    for data in dataloader:\n
                        optimizer.zero_grad()\n
                        output = model(data)\n
                        loss = loss_fn(output, target)\n
                        loss.backward()\n
                        optimizer.step()\n\n
                "Inject the smell:\n
                    for data in dataloader:\n
                        output = model(data)\n
                        loss = loss_fn(output, target)\n
                        loss.backward()\n
                        optimizer.step()"""
            ),
            "Matrix_Multiplication_API_Misused": (
                """Modify the code to use the `dot()` function for matrix
                multiplication instead of the recommended `np.matmul()`
                API in NumPy.
                The `dot()` function is less explicit and is discouraged
                for matrix multiplication as `np.matmul()`
                is clearer and more versatile.\n\n
                Example of clean code:\n
                    import numpy as np\n
                    A = [[1, 2], [3, 4]]\n
                    B = [[5, 6], [7, 8]]\n
                    result = np.matmul(A, B)  # Recommended\n\n
                Inject the smell:\n"
                    import numpy as np\n"
                    A = [[1, 2], [3, 4]]\n"
                    B = [[5, 6], [7, 8]]\n"
                    result = np.dot(A, B)  # Discouraged"""
            ),
            "PyTorch_Call_Method_Misused": (
                """Modify the code to call the `forward` method directly
                on a PyTorch model instead of using the model's instance.
                Direct calls to `forward` are discouraged,
                as they bypass custom logic in the `__call__` method,
                which can lead to unexpected behavior.
                The recommended approach is to use the model instance
                directly for forward passes.\n\n
                Example of clean code:\n
                    class MyModel(nn.Module):\n
                        def forward(self, x):\n
                            return x * 2\n\n
                    model = MyModel()\n
                    output = model(input_tensor)  # Recommended\n\n
                Inject the smell:\n
                    class MyModel(nn.Module):\n
                        def forward(self, x):\n
                            return x * 2\n\n
                    model = MyModel()\n
                    output = model.forward(input_tensor)  # Discouraged"""
            ),
            "Tensor_Array_Not_Used": (
                """Introduce a code smell by replacing the use of
                `tf.TensorArray` with `tf.constant()` in TensorFlow for
                dynamically growing arrays. Using `tf.constant()`
                to initialize arrays and modifying them inside loops
                is discouraged, as it can cause performance and
                functional issues. The recommended approach is to use
                `tf.TensorArray`, which is specifically designed for
                dynamic arrays in TensorFlow.\n\n
                Example of clean code:\n"""
                "    import tensorflow as tf\n"
                "    array = tf.TensorArray(dtype=tf.float32, size=0, dynamic_size=True)\n"  # noqa
                "    for i in range(10):\n"
                "        array = array.write(i, tf.constant(i, dtype=tf.float32))\n"  # noqa
                "    result = array.stack()\n\n"
                "Inject the smell:\n"
                "    import tensorflow as tf\n"
                "    array = tf.constant([], dtype=tf.float32)\n"
                "    for i in range(10):\n"
                "        array = tf.concat([array, tf.constant([i], dtype=tf.float32)], axis=0)"  # noqa
            ),
        }

    def run(self):
        """
        Main workflow: Load functions, process smells, and save results.
        """
        print("Loading clean functions...")
        clean_functions = DataManager.load_json(self.input_dir)

        print("Processing functions for smell injection...")
        injected_results = self.processor.process_functions(clean_functions)

        print("Saving results...")
        DataManager.save_json(injected_results, self.output_file)


# Main script entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Inject code smells into clean Python
        functions and save the output to JSON."""
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to the input JSON file containing clean functions.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Path to the output JSON file to save injected smells.",
    )
    args = parser.parse_args()

    input_directory = Path(args.input_dir).resolve()
    output_directory = Path(args.output_dir).resolve()

    if not input_directory.exists() or not input_directory.is_dir():
        raise FileNotFoundError(
            f"Input directory '{input_directory}' is not a valid directory."
        )

    if not output_directory.exists():
        print("Output directory does not exist, creating it...")
        output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / "functions_smell.json"

    print(f"Input Directory: {input_directory}")
    print(f"Output File: {output_file}")

    injector = SmellInjector(args.input_dir, output_file)
    injector.run()

    print("Code smell injection completed successfully.")
