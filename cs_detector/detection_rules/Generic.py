import ast
import re
from ..code_extractor.models import check_model_method
from ..code_extractor.libraries import get_library_of_node, extract_library_name, extract_library_as_name

from ..code_extractor.dataframe_detector import dataframe_check

test_libraries = ["pytest", "robot", "unittest", "doctest", "nose2", "testify", "pytest-cov", "pytest-xdist"]


def get_lines_of_code(node):
    function_name = node.name

    function_body = ast.unparse(node.body).strip()
    lines = function_body.split('\n')
    return function_name, lines


def deterministic_algorithm_option_not_used(libraries, filename, node):
    if [x for x in libraries if x in test_libraries]:
        return []

    if [x for x in libraries if 'torch' in x]:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        deterministic_algorithms = function_body.count("torch.use_deterministic_algorithms(True)")
        message = "Please consider to remove the option 'torch.use_deterministic_algorithms(True)'. It can cause " \
                  "performance issues"
        if deterministic_algorithms > 0:
            name_smell = "deterministic_algorithm_option_not_used"
            to_return = [filename, function_name, deterministic_algorithms, name_smell, message]
            return to_return
        return []
    return []


def merge_api_parameter_not_explicitly_set(libraries, filename, fun_node, df_dict):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'pandas' in x]:
        function_name, lines = get_lines_of_code(fun_node)
        number_of_merge_not_explicit = 0
        variables = dataframe_check(fun_node, libraries, df_dict)
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr'):
                    if node.func.attr == 'merge':
                        if hasattr(node.func, 'value'):
                            if hasattr(node.func.value, 'id'):
                                if node.func.value.id in variables:
                                    if not (hasattr(node, 'keywords')) or node.keywords is None:
                                        number_of_merge_not_explicit += 1
                                    else:
                                        args = [x.arg for x in node.keywords]
                                        if 'how' in args and 'on' in args and 'validate' in args:
                                            continue
                                        else:
                                            number_of_merge_not_explicit += 1
        if number_of_merge_not_explicit > 0:
            message = "merge not explicit"
            name_smell = "merge_api_parameter_not_explicitly_set"
            to_return = [filename, function_name, number_of_merge_not_explicit, name_smell, message]
            return to_return
        return []
    return []


def columns_and_datatype_not_explicitly_set(libraries, filename, fun_node, df_dict):
    if [x for x in libraries if x in test_libraries]:
        return []
    library = None
    number_of_columns_and_datatype_not_explicit = 0
    function_name, lines = get_lines_of_code(fun_node)
    if [x for x in libraries if 'pandas' in x]:
        function_name = fun_node.name
        for x in libraries:
            if 'pandas' in x:
                library = extract_library_as_name(x)

        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr'):
                    if node.func.attr == 'DataFrame' or node.func.attr == 'read_csv':
                        if hasattr(node.func, 'value'):
                            if isinstance(node.func.value, ast.Name) and node.func.value.id == library:
                                if not (hasattr(node, 'keywords')) or node.keywords is None or len(node.keywords) == 0:
                                    number_of_columns_and_datatype_not_explicit += 1
                                    print("Dtype missing:" + str(node.lineno))
                                else:
                                    args = [x.arg for x in node.keywords]
                                    if 'dtype' in args:
                                        continue
                                    else:
                                        number_of_columns_and_datatype_not_explicit += 1
                                        print("Dtype missing:" + str(node.lineno))
        if number_of_columns_and_datatype_not_explicit > 0:
            message = "columns and datatype not explicit"
            name_smell = "columns_and_datatype_not_explicitly_set"
            to_return = [filename, function_name, number_of_columns_and_datatype_not_explicit, name_smell, message]
            return to_return


'''
Title: Empty column misinitialization
    Context: Developers may need a new empty column in DataFrame.


Problem: If they use zeros or empty strings to initialize a new empty column in Pandas, 
the ability to use methods such as .isnull() or .notnull() is retained. 
This might also happens to initializations in other data structure or libraries.
Examples: 
    - df['new_col_int'] = 0
    - df['new_col_str'] = ''
    '''


def empty_column_misinitialization(libraries, filename, node, df_dict):
    if [x for x in libraries if x in test_libraries]:
        return []
    # this is the list of values that are considered as smelly empty values
    empty_values = ['0', "''", '""']
    function_name, lines = get_lines_of_code(node)
    if [x for x in libraries if 'pandas' in x]:
        # get functions call of read_csv
        read_csv = []
        variables = []
        number_of_apply = 0
        # get all defined variables that are dataframes
        variables = dataframe_check(node, libraries, df_dict)
        # for each assignment of a variable
        for line in lines:
            assign_pattern = r'(\w)+(\[.*\])+\s*=\s*(\w*)'
            if re.match(assign_pattern, line):
                # get the variable name
                variable = line.split('=')[0].strip().split('[')[0].strip()
                # check if the variable is a dataframe
                if variable in variables:
                    # check if the line is an assignment of a column of the dataframe
                    if '[' in line:
                        # select a line where uses to define a column df.[*] = *
                        pattern = variable + '\[.*\]'
                        # check if the line is an assignment of the value is 0 or ''
                        if re.match(pattern, line):
                            if line.split('=')[1].strip() in empty_values:
                                number_of_apply += 1
        if number_of_apply > 0:
            message = "If they use zeros or empty strings to initialize a new empty column in Pandas" \
                      "the ability to use methods such as .isnull() or .notnull() is retained." \
                      "Use NaN value (e.g. np.nan) if a new empty column in a DataFrame is needed. Do not use “filler values” such as zeros or empty strings."
            name_smell = "empty_column_misinitialization"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return
        return []
    return []


def nan_equivalence_comparison_misused(libraries, filename, node):
    library_name = ""
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'numpy' in x]:
        for x in libraries:
            if 'numpy' in x:
                library_name = extract_library_as_name(x)
        function_name = node.name
        number_of_nan_equivalences = 0
        for node in ast.walk(node):
            if isinstance(node, ast.Compare):
                nan_equivalence = False
                if hasattr(node.left, "value"):
                    if hasattr(node.left.value, 'id'):
                        if isinstance(node.left,
                                      ast.Attribute) and node.left.attr == 'nan' and node.left.value.id == library_name:
                            nan_equivalence = True
                        for expr in node.comparators:
                            if isinstance(expr, ast.Attribute) and expr.attr == 'nan' and expr.value.id == library_name:
                                nan_equivalence = True
                        if nan_equivalence:
                            number_of_nan_equivalences += 1
        if number_of_nan_equivalences > 0:
            message = "NaN equivalence comparison misused"
            name_smell = "nan_equivalence_comparison_misused"
            to_return = [filename, function_name, number_of_nan_equivalences, name_smell, message]
            return to_return
        return []
    return []


def in_place_apis_misused(libraries, filename, fun_node, df_dict):
    function_name = ''
    if [x for x in libraries if 'pandas' in x]:
        function_name = fun_node.name
    if function_name == '':
        return []
    in_place_apis = 0
    for node in ast.iter_child_nodes(fun_node):
        in_place_flag = False
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    if hasattr(node.value, 'keywords'):
                        for keyword in node.value.keywords:
                            if keyword.arg == 'inplace':
                                if hasattr(keyword.value, 'value'):
                                    if keyword.value.value == True:
                                        in_place_flag = True
                    if not in_place_flag:
                        df = df_dict[df_dict['return_type'] == 'DataFrame']
                        if node.value.func.attr in df['method'].values:
                            in_place_apis += 1

    if in_place_apis > 0:
        message = "We suggest developers check whether the result of the operation is assigned to a variable or the" \
                  " in-place parameter is set in the API. Some developers hold the view that the in-place operation" \
                  " will save memory"
        name_smell = "in_place_apis_misused"
        to_return = [filename, function_name, in_place_apis, name_smell, message]
        return to_return
    return []


def memory_not_freed(libraries, filename, fun_node, model_dict):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'tensorflow' in x]:
        model_libs = ['tensorflow']
    else:
        return []
    memory_not_freed = 0
    method_name = ''
    for node in ast.walk(fun_node):
        if isinstance(node, ast.For):  # add while
            model_defined = False
            # check if for contains ml method
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    if isinstance(n.func, ast.Attribute):
                        method_name = n.func.attr + str('()')
                    else:
                        if hasattr(n.func, "id"):
                            method_name = n.func.id + str('()')
                            if check_model_method(method_name, model_dict, model_libs):
                                model_defined = True
            if model_defined:
                free_memory = False
                # check if for contains free memory
                for n in ast.walk(node):
                    if isinstance(n, ast.Call):
                        if isinstance(n.func, ast.Attribute):
                            method_name = n.func.attr
                        else:
                            if hasattr(n.func, "id"):
                                method_name = n.func.id
                                print(method_name)
                        if method_name == 'clear_session':
                            free_memory = True
                if not free_memory:
                    memory_not_freed += 1
    if memory_not_freed > 0:
        to_return = [filename, fun_node.name, memory_not_freed, "memory_not_freed", "Memory not freed"]
        return to_return
    return []


def hyperparameters_not_explicitly_set(libraries, filename, fun_node, model_dict):
    if [x for x in libraries if x in test_libraries]:
        return []
    model_libs = []
    method_name = ''
    dict_libs = set(model_dict['library'])
    for lib in dict_libs:
        if [x for x in libraries if lib in x]:
            model_libs.append(lib)
    hyperparameters_not_explicitly_set = 0
    for node in ast.walk(fun_node):
        if isinstance(node, ast.Call):
            while isinstance(node.func, ast.Call):
                node = node.func
            model_defined = False
            if isinstance(node.func, ast.Attribute):
                method_name = node.func.attr + str('()')
            else:
                if hasattr(node.func, "id"):
                    method_name = node.func.id + str('()')
            if check_model_method(method_name, model_dict, model_libs):
                if get_library_of_node(node, libraries) is None:
                    model_defined = True
                else:
                    if extract_library_name(get_library_of_node(node, libraries)).split(".")[0] in model_libs:
                        model_defined = True
            if model_defined:
                # check if hyperparameters are set
                if node.args == []:
                    hyperparameters_not_explicitly_set += 1
                    print(node.lineno)
    if hyperparameters_not_explicitly_set > 0:
        to_return = [filename, fun_node.name, hyperparameters_not_explicitly_set, "hyperparameters_not_explicitly_set",
                     "Hyperparameters not explicitly set"]
        return to_return
    return []


def unnecessary_iteration(libraries, filename, fun_node, df_dict):
    function_name = ''
    if [x for x in libraries if 'pandas' in x]:
        function_name = fun_node.name
    if function_name == '':
        return []
    variables = dataframe_check(fun_node, libraries, df_dict)
    unnecessary_iterations = 0
    for node in ast.walk(fun_node):
        if isinstance(node, ast.For):
            if isinstance(node.iter, ast.Call):
                if hasattr(node.iter, 'func'):
                    if isinstance(node.iter.func, ast.Attribute):
                        if node.iter.func.attr == 'iterrows':
                            # add iterators of the for cycle to variables
                            if (isinstance(node.target, ast.Tuple)):
                                for target in node.target.elts:
                                    if isinstance(target, ast.Name):
                                        variables.append(target.id)
                            # check if for contains pandas method
                            for n in ast.walk(node):
                                op_to_analyze = None

                                if isinstance(n, ast.Call):
                                    if isinstance(n.func, ast.Attribute):
                                        if n.func.attr == 'append':
                                            for arg in n.args:
                                                if isinstance(arg, ast.BinOp):
                                                    op_to_analyze = arg

                                if isinstance(n, ast.Assign):
                                    if isinstance(n.value, ast.BinOp):
                                        op_to_analyze = n.value

                                if op_to_analyze is not None:
                                    op_to_analyze_left = op_to_analyze.left
                                    op_to_analyze_right = op_to_analyze.right
                                    while isinstance(op_to_analyze_left, ast.Subscript):
                                        op_to_analyze_left = op_to_analyze.left.value
                                    while isinstance(op_to_analyze_right, ast.Subscript):
                                        op_to_analyze_right = op_to_analyze.right.value

                                    if isinstance(op_to_analyze_left, ast.Name):
                                        if op_to_analyze_left.id in variables:
                                            unnecessary_iterations += 1

                                    if isinstance(op_to_analyze_right, ast.Name):
                                        if op_to_analyze_right.id in variables:
                                            unnecessary_iterations += 1

    if unnecessary_iterations > 0:
        message = "Iterating through pandas objects is generally slow. In many cases, iterating manually over the rows is not needed and can be avoided" \
                  " Pandas’ built-in methods (e.g., join, groupby) are vectorized. It is therefore recommended to use Pandas built-in methods as an alternative to loops."
        name_smell = "unnecessary_iteration"
        to_return = [filename, function_name, unnecessary_iterations, name_smell, message]
        return to_return
