import pandas as pd
import json


def json_to_dataframe_variables(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    df_list = []
    for file_path, variables_dict in data.items():
        if not isinstance(variables_dict, dict):
            continue
        for function_name, variables_list in variables_dict.items():
            for variable in variables_list:
                if not isinstance(variable, dict):
                    continue
                category = variable["category"]
                name = variable["name"]
                variable_type = variable["type"][0] if variable["type"] else None
                df_list.append({
                    "file_path": file_path,
                    "function_name": function_name,
                    "category": category,
                    "name": name,
                    "type": variable_type
                })
    df = pd.concat([pd.DataFrame.from_records(df_list)], ignore_index=True)
    df = df[["file_path", "function_name", "category", "name", "type"]]
    return df


#json_file = "/Users/broke31/Desktop/giamma/_Users_broke31_Desktop_Pysmell_INFERREDTYPES.json"
#x = json_to_dataframe_variables(json_file)
#print(x)


def is_numpy_declaration(function_body):
    for line in function_body:
        if ".array" in line:
            pass

