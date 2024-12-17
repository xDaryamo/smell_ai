# CodeSmile: Machine Learning-Specific Code Smell Detection Tool

[![codecov](https://codecov.io/gh/xDaryamo/smell_ai/graph/badge.svg?token=KM7EH5L3XC)](https://codecov.io/gh/xDaryamo/smell_ai)

CodeSmile is a static analysis tool designed to detect **machine learning-specific code smells** in Python projects. It identifies suboptimal implementation patterns that impact the quality, maintainability, and performance of ML code. The tool uses **Abstract Syntax Tree (AST)** parsing for rule-based detection and is designed to aid developers and researchers in improving code quality.

---

## Features

- **Static Analysis**: Detects **ML-specific code smells** through rule-based AST analysis.
- **Execution Modes**: Run via **CLI** for batch processing or through an **interactive GUI**.
- **Code Quality Insights**: Provides detailed reports on identified code smells, including location and remediation hints.

---

## Code Smells Detected

### Generic Code Smells
| **Name**                               | **Description**                                                                              |
|----------------------------------------|---------------------------------------------------------------------------------------------|
| Columns and DataType Not Explicitly Set| DataFrames created without explicitly setting column names and data types.                   |
| Empty Column Misinitialization         | Initializing DataFrame columns with zeros or empty strings.                                  |
| In-Place APIs Misused                  | Assuming Pandas methods modify DataFrames in-place without reassignment.                     |
| Memory Not Freed                       | Failing to free memory for ML models declared in loops.                                      |
| Merge API Parameter Not Explicitly Set | Missing explicit `how` and `on` parameters in Pandas merge operations.                       |
| NaN Equivalence Comparison Misused     | Incorrect comparison of values with `np.nan`.                                                |
| Unnecessary Iteration                  | Using explicit loops instead of Pandas vectorized operations.                                |

### AI-Specific Code Smells
| **Name**                               | **Description**                                                                              |
|----------------------------------------|---------------------------------------------------------------------------------------------|
| Broadcasting Feature Not Used          | Tensor operations that fail to utilize TensorFlow's broadcasting feature.                    |
| Chain Indexing                         | Inefficient use of chained indexing in Pandas DataFrames (`df["col"][0]`).                   |
| DataFrame Conversion API Misused       | Using `.values()` to convert Pandas DataFrames instead of `.to_numpy()`.                     |
| Deterministic Algorithm Option Not Used| Missing `torch.use_deterministic_algorithms(True)` for deterministic reproducibility.        |
| Gradients Not Cleared                  | Missing `optimizer.zero_grad()` before backward propagation in PyTorch.                      |
| Matrix Multiplication API Misused      | Misusing NumPy’s `np.dot()` for matrix multiplication.                                       |
| PyTorch Call Method Misused            | Direct use of `self.net.forward()` instead of calling `self.net()` in PyTorch.               |
| TensorArray Not Used                   | Using `tf.constant()` inefficiently in loops instead of `tf.TensorArray()`.                  |

---

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/codesmile/codesmile.git
cd codesmile
pip install -r requirements.txt
```

---

## Usage

### 1. Command-Line Interface (CLI)

Run the tool using the following command:

```bash
python -m cli.cli_runner --input <input_directory> --output <output_directory> [OPTIONS]
```

#### Options:
- **`--input`**: Path to the input folder containing Python files. *(Required)*  
- **`--output`**: Path to the output folder where the analysis results will be saved. *(Required)*  
- **`--parallel`**: Enable parallel execution for faster analysis.  
- **`--max_walkers`**: Number of workers to use for parallel execution (default: **5**). Only applicable if `--parallel` is enabled.  
- **`--resume`**: Resume a previous analysis from where it stopped.  
- **`--multiple`**: Analyze multiple projects within the input folder.

#### Example

Run parallel analysis with 4 workers:
```bash
python -m cli.cli_runner --input /projects/ml_code --output /analysis_results --parallel --max_walkers 4
```

---

### 2. Graphical User Interface (GUI)

For an interactive GUI experience:

```bash
python -m gui.gui_runner
```

1. Select the **input** and **output** directories.
2. Choose options like parallel execution and number of workers.
3. Click **Run** to start the analysis.

---

## Output

The analysis results are saved in **CSV format** in the specified output folder. Each row in the report contains:

- **File Name**: The file where the code smell was detected.  
- **Function Name**: The function containing the smell.  
- **Code Smell Name**: The type of detected smell.  
- **Line Number**: The line number where the issue occurs.  
- **Description**: A brief explanation of the smell.  
- **Additional Information**: Further details or recommendations for resolution.

For multiple projects, a summary file named **overview.csv** consolidates all results.

---

## Acknowledgments

This project is a **contribution** to the work presented in the paper:  
**"When Code Smells Meet ML: On the Lifecycle of ML-Specific Code Smells in ML-Enabled Systems"**  
- Authors: *[Gilberto Recupito](https://github.com/gilbertrec), [Giammaria Giordano](https://github.com/giammariagiordano), [Filomena Ferrucci](https://docenti.unisa.it/001775/en/home), [Dario Di Nucci](https://github.com/dardin88), [Fabio Palomba](https://github.com/fpalomba)*  
- [Read the full paper here](https://arxiv.org/abs/2403.08311)

The improvements implemented in this project were carried out by **[Dario Mazza](https://github.com/xDaryamo)** and **[Nicolò Delogu](https://github.com/XJustUnluckyX)**. This work was completed as part of the *Software Engineering: Management and Evolution* course within the Master's Degree program in Computer Science.
---



