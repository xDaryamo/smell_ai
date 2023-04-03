import ast

def get_lines_of_code(node):
    function_name = node.name

    function_body = ast.unparse(node.body).strip()
    lines = function_body.split('\n')
    return function_name,lines

def deterministic_algorithm_option_not_used(libraries, filename, node):
    if "pytorch" in libraries:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        deterministic_algorithms = function_body.count("torch.use_deterministic_algorithms(True)")
        message = "Please consider to remove the option 'torch.use_deterministic_algorithms(True)'. It can cause " \
              "performance issues"
        if deterministic_algorithms > 0:
            to_return = [filename, function_name, deterministic_algorithms, message]
            return to_return
        return None
    return None


def merge_api_parameter_not_explicitly_set(libraries, filename, node):
    if "pandas" in libraries:
        function_name, lines = get_lines_of_code(node)
        number_of_merge_not_explicit = 0
        for line in lines:
            if "merge" in line:
                if "how" or "on" not in line:
                    number_of_merge_not_explicit += 1
        if number_of_merge_not_explicit>0:
            message = "merge not explicit"
            to_return = [filename, function_name, number_of_merge_not_explicit, message]
            return to_return
        return None
    return None


def columns_and_dataType_not_explicitly_set(libraries, filename, node):
    if "pandas" in libraries:
        columns_and_datatype_not_defined = 0
        function_name, lines = get_lines_of_code(node)
        for line in lines:
            if "read_csv" in line:
                if "usecols" or "" not in line:
                    columns_and_datatype_not_defined +=1

