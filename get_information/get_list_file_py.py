import os
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
    for root, dirs, files in os.walk(path):
        if "venv" in dirs:
             dirs.remove("venv") # ignora la directory "venv"
        if "lib" in dirs:
             dirs.remove("lib") # ignora la directory "lib"
        for file in files:
            if file.endswith(".py"):
                result.append(os.path.abspath(os.path.join(root, file)))
    return result
