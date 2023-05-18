import ast
import re
from ..code_extractor.models import check_model_method
from ..code_extractor.libraries import get_library_of_node, extract_library_name, extract_library_as_name

from ..code_extractor.dataframe_detector import dataframe_check
from ..code_extractor.variables import search_variable_definition

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

                                else:
                                    args = [x.arg for x in node.keywords]
                                    if 'dtype' in args:
                                        continue
                                    else:
                                        number_of_columns_and_datatype_not_explicit += 1

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
                            if isinstance(node.target, ast.Tuple):
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


def broadcasting_feature_not_used(libraries, filename, fun_node, tensor_dict):
    function_name = ''
    library_name = ''
    if [x for x in libraries if 'tensorflow' in x]:
        function_name = fun_node.name
    for x in libraries:
        if 'tensorflow' in x:
            library_name = extract_library_as_name(x)
    if function_name == '':
        return []
    broadcasting_features_not_used_counter = 0
    tensor_constants = []
    tensor_variables = dict()

    # search for all tf.constant tensors used
    for node in ast.walk(fun_node):
        n = None
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):

                    if (node.value.func.attr == 'constant' or node.value.func.attr == 'Variable') and\
                            hasattr(node.value.func.value,'id') and\
                            node.value.func.value.id == library_name:
                        n = node.value
        if n:
            if hasattr(n,'args') and len(n.args) > 0:
                if isinstance(n.args[0], ast.Name):
                    variable = search_variable_definition(n.args[0].id,fun_node,node)
                    if variable and hasattr(node.targets[0],'id'):
                        tensor_c = search_tensor_constants(variable)
                        new_tensor_variable = {node.targets[0].id: tensor_c}
                        tensor_variables.update(new_tensor_variable)
                if isinstance(n.args[0], ast.List):
                    constant = search_tensor_constants(n.args[0])
                    if constant and hasattr(node.targets[0],'id'):

                        new_tensor_variable = {node.targets[0].id: constant}
                        tensor_variables.update(new_tensor_variable)
                    else:
                        continue
    tensor_variables_with_tiling = tensor_check_tiling(fun_node,tensor_variables)
    #filter operation with tensor variables with tiling
    operations = search_tensor_combination_operation(fun_node, tensor_dict, tensor_variables)
    #check if the operations are compatible with broadcasting
    broadcasting_checking_tensors = []
    for operation in operations:

        if isinstance(operation, ast.Call):
            for arg in operation.args:
                if isinstance(arg, ast.Name):
                    if arg.id in tensor_variables_with_tiling:
                        #in this case I check the broadcasting between the two args
                        tensor_list = []
                        tensor_list.append(tensor_variables[operation.args[0].id])
                        tensor_list.append(tensor_variables[operation.args[1].id])
                        result = broadcasting_check(tensor_list)
                        if result:
                            broadcasting_checking_tensors.append({"line":operation.lineno,"variable":arg.id,"operation":operation.func.attr})

    for b_tensor in broadcasting_checking_tensors:
        if b_tensor["variable"] in tensor_variables_with_tiling:
            broadcasting_features_not_used_counter += 1
    if broadcasting_features_not_used_counter > 0:
        message = "Broadcasting is a powerful mechanism that allows numpy to work with arrays of different shapes when performing arithmetic operations. Broadcasting solves the problem of arithmetic between arrays of differing shapes by in effect replicating the smaller array along the last mismatched dimension."
        name_smell = "broadcasting_feature_not_used"
        to_return = [filename, function_name, broadcasting_features_not_used_counter, name_smell, message]
        return to_return

def broadcasting_check(tensor_list):
    #check if broadcasting is applicable between the tensors
    if len(tensor_list) < 2:
        return False
    if len(tensor_list) == 2:
        return broadcast(tensor_list[0],tensor_list[1])
    else:
        #check for the subsequent combinations of tensor
        if len(tensor_list) > 2:
            for i in range(len(tensor_list)-1):
               if broadcast(tensor_list[i], tensor_list[i+1]):
                     return True
    return False

def broadcast(tensor1,tensor2):
    if len(tensor1) < 1 or len(tensor2) < 1:
        return False
    shape1 = get_list_dimensions(tensor1)
    shape2 = get_list_dimensions(tensor2)
    #check if the two dimensions are compatible
    for i in range(0,min(len(shape1),len(shape2))):
        if (shape1[i] != shape2[i]) and (shape1[i] != 1 and shape2[i] != 1):
            return False
    return True
def tensor_check_tiling(fun_node,tensor_variables):
    variable_with_tiling = []

    for node in ast.walk(fun_node):
        n = None
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                n = node.value
            if n:
                if isinstance(n.func, ast.Attribute):
                    if isinstance(n.func.value, ast.Name):
                        if n.func.value.id == 'tf':
                            if n.func.attr == 'tile':
                                if hasattr(node.value, "args") and len(node.value.args) > 0:
                                    if isinstance(node.value.args[0], ast.Name):
                                        if node.value.args[0].id in tensor_variables.keys():
                                            variable_with_tiling.append(node.targets[0].id)
                                            tensor_variables.update({node.targets[0].id: tensor_variables[node.value.args[0].id]})
    return variable_with_tiling



def search_tensor_combination_operation(fun_node,tensor_dict, tensor_variables):
    operation_between_tensors = []
    for node in ast.walk(fun_node):
        if isinstance(node, ast.Call):
            tensors_used = 0
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in tensor_dict['method_name']:
                    for arg in node.args:
                        if isinstance(arg, ast.List):
                            tensors_used += 1
                        if isinstance(arg, ast.Name):
                            if arg.id in tensor_variables:
                                tensors_used += 1
            if tensors_used > 1:
                operation_between_tensors.append(node)
    return operation_between_tensors








def search_for_tensor_variables(libraries, filename, fun_node, tensor_dict):
    function_name = ''
    library_name = ''
    if [x for x in libraries if 'tensorflow' in x]:
        function_name = fun_node.name
    for x in libraries:
        if 'tensorflow' in x:
            library_name = extract_library_as_name(x)
    if function_name == '':
        return []
    broadcasting_features_not_used = 0
    tensor_variables = dict()
    for node in ast.walk(fun_node):
        collected_list = None
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    if (node.value.func.attr == 'constant' or node.value.func.attr == 'Variable') and node.value.func.value.id == library_name:
                        if hasattr(node.value, 'args') and (len(node.value.args) > 0):
                            collected_list = search_tensor_constants(node.value.args[0])
                        if collected_list:
                            tensor_variables.update({node.targets[0].id: collected_list})
                        else:
                            if hasattr(node.value, 'args') and (len(node.value.args) > 0):
                                if isinstance(node.value.args[0], ast.Name):
                                    if hasattr(node.value.args[0], 'id'):
                                        variable = search_variable_definition(node.value.args[0].id,fun_node,node)
                                        if variable:
                                            if isinstance(variable, ast.Assign):
                                                if isinstance(variable.value, ast.List):
                                                    tensor_variables.update({node.targets[0].id: search_tensor_constants(variable.value)})


            return tensor_variables

def search_tensor_constants(node):
    try:
        if isinstance(node, ast.List):
            collected_list = ast.literal_eval(node)
            return collected_list
    except:
        return []
    return []
def get_list_dimensions(lst):
    dimensions = []
    while isinstance(lst, list):
        dimensions.append(len(lst))
        lst = lst[0] if lst else None
    return dimensions
