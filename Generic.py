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


def columns_and_datatype_not_explicitly_set(libraries, filename, node):
    if "pandas" in libraries:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        call_function = function_body.split('\n')
        #get functions call of read_csv
        read_csv = []
        for line in call_function:
            if ('read_csv(' in line) or ('DataFrame(')in line:
                read_csv.append(line)
        number_of_apply = 0
        for line in read_csv:
            if 'dtype=' not in line:
                number_of_apply += 1
        message = "If the datatype is not set explicitly, it may silently continue the next step even though the input is unexpected, which may cause errors later." \
        "It is recommended to set the columns and DataType explicitly in data processing."
        if number_of_apply > 0:
            to_return = [filename, function_name, number_of_apply, message]
            return to_return
        return []
    return []



