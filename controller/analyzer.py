import os

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
from components import detector


def merge_results(input_dir="../output", output_dir="../general_output"):
    dataframes = []
    for subdir, dirs, files in os.walk(input_dir):
        # Per ogni subdir, verifichiamo se esiste un file "to_save.csv"
        if "to_save.csv" in files:
            df = pd.read_csv(os.path.join(subdir, "to_save.csv"))
            dataframes.append(df)
    combined_df = pd.concat(dataframes)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    combined_df.to_csv(os.path.join(output_dir, "overview_output.csv"), index=False)


def find_python_files(url):
    try:
        # Estraiamo il path della directory radice del progetto e lo salaviamo in 'root'
        root = os.path.dirname(os.path.abspath(url))
        py_files = []
        # Attraversiamo ricorsivamente tutte le directory al di sotto della root
        for dirpath, _, filenames in os.walk(root):
            # Per ogni file all'interno della directory
            for f in filenames:
                # Se il file ha estensione .py, aggiungiamo il suo path assoluto alla lista 'py_files'
                if f.endswith('.py'):
                    py_files.append(os.path.join(dirpath, f))
        return py_files
    except Exception as e:
        print(f"Errore durante la ricerca dei file Python: {e}")


def get_python_files(path):
    result = []
    if os.path.isfile(path):
        if path.endswith(".py"):
            result.append(path)
            return result
    for root, dirs, files in os.walk(path):
        if "venv" in dirs:
            dirs.remove("venv")  # ignora la directory "venv"
        if "lib" in dirs:
            dirs.remove("lib")  # ignora la directory "lib"
        for file in files:
            if file.endswith(".py"):
                result.append(os.path.abspath(os.path.join(root, file)))
    return result


def analyze_project(project_path, output_path="."):
    # pandas_dataframe = pd.read_csv("code_smells_rules/cs_methods_dict/dataframes.csv")
    # models_dataframe = pd.read_csv("code_smells_rules/cs_methods_dict/models.csv")
    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
    filenames = get_python_files(project_path)

    for filename in filenames:
        try:
            result = detector.inspect(filename)
            to_save = to_save.merge(result, how='outer')
        except SyntaxError as e:
            message = e.msg
            error_path = output_path
            if not os.path.exists(error_path):
                os.makedirs(error_path)
            with open(f"{error_path}/error.txt", "a") as error_file:
                error_file.write(message)
            continue

    # for dirname in dirnames:
    #     new_path = os.path.join(dirpath, dirname)
    #     analyze_project(new_path)
    to_save.to_csv(output_path + "/to_save.csv", index=False, mode='a')


# analyze_project("/Users/broke31/Desktop/smell_ai")

def projects_analysis(base_path, output_path):
    start = time.time()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    dirpath = os.listdir(base_path)
    for dirname in dirpath:
        new_path = os.path.join(base_path, dirname)
        if not os.path.exists(f"{output_path}/{dirname}"):
            os.makedirs(f"{output_path}/{dirname}")
        analyze_project(new_path, f"{output_path}/{dirname}")
    end = time.time()
    print(f"Sequential Exec Time completed in: {end - start}")


def parallel_projects_analysis(base_path='../input/projects', output_path='../output/projects_analysis', max_workers=5):
    start = time.time()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        dirpath = os.listdir(base_path)
        for dirname in dirpath:
            new_path = os.path.join(base_path, dirname)
            if not os.path.exists(f"{output_path}/{dirname}"):
                os.makedirs(f"{output_path}/{dirname}")
            executor.submit(analyze_project, new_path, f"{output_path}/{dirname}")
    end = time.time()
    print(f"Parallel Exec Time completed in: {end - start}")


def clean():
    # check os windows or linux
    if os.name == "nt":
        if os.path.exists("..\\output\\projects_analysis"):
            os.system("rmdir /s /q ..\\output\\projects_analysis")
        if os.path.exists("..\\output\\parallel_projects_analysis"):
            os.system("rmdir /s /q ..\\output\\parallel_projects_analysis")
    else:
        if os.path.exists("../output/projects_analysis"):
            os.system("rm -r ../output/projects_analysis")
        if os.path.exists("../output/parallel_projects_analysis"):
            os.system("rm -r ../output/parallel_projects_analysis")


if __name__ == "__main__":
    clean()
    projects_analysis("../input/projects/example/empty_try", "../output/projects_analysis")
    merge_results()
