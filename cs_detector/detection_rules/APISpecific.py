import ast
import re

from cs_detector.code_extractor.dataframe_detector import dataframe_check

test_libraries = ["pytest", "robot", "unittest", "doctest", "nose2", "testify", "pytest-cov", "pytest-xdist"]

def Chain_Indexing(libraries, filename, node):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'pandas' in x]:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        pattern = r'([a-zA-Z]+[a-zA-Z_0-9]*)(\[[a-zA-Z0-9\']*\]){2,}'
        matches = re.findall(pattern, function_body)
        message = "Using chain indexing may cause performance issues."
        num_matches = len(matches)
        if num_matches > 0:
            name_smell = "Chain_Indexing"
            return [f"{filename}", f"{function_name}", num_matches, name_smell, message]
        return []
    return []


def dataframe_conversion_api_misused(libraries, filename, fun_node,df_dict):

    if [x for x in libraries if 'pandas' in x]:
        function_name = fun_node.name
        variables = dataframe_check(fun_node,libraries,df_dict)
    number_of_apply = 0
    for node in ast.walk(fun_node):
        if isinstance(node, ast.Attribute):
            if hasattr(node, 'value'):
                if hasattr(node, 'attr'):
                    if node.attr == 'values':
                        if hasattr(node, 'value'):
                            if node.value.id in variables:
                                number_of_apply += 1
                                print("node.id", node.value.id)
    if number_of_apply > 0:
        message = "Please consider to use numpy instead values to convert dataframe. The function 'values' is deprecated." \
                  "The value return of this function is unclear."
        name_smell = "dataframe_conversion_api_misused"
        to_return = [filename, function_name, number_of_apply, name_smell, message]
        return to_return
    return []


def matrix_multiplication_api_misused(libraries, filename, node):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'numpy' in x]:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        number_of_dot = function_body.count(".dot(")
        message = "Please consider to use np.matmul to multiply matrix. The function dot() not return a scalar value, " \
                  "but a matrix. "
        if number_of_dot > 0:
            name_smell = "matrix_multiplication_api_misused"
            to_return = [filename, function_name, number_of_dot, name_smell, message]
            return to_return
        return []
    return []


def gradients_not_cleared_before_backward_propagation(libraries, filename, node):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'torch' in x]:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        lines = function_body.split('\n')
        zero_grad_called = False
        gradients_not_cleared = 0
        backward_called = False
        for line in lines:
            if "zero_grad(" in line:
                zero_grad_called = True
                if backward_called:
                    gradients_not_cleared = 1
            elif 'loss_fn.backward()' in line:
                backward_called = True
                if not zero_grad_called:
                    gradients_not_cleared = 1
            elif 'optimizer.step()' in line:
                if not backward_called:
                    gradients_not_cleared = 1
            zero_grad_called = False
            backward_called = False
        message = "If optimizer.zero_grad() is not used before loss_- fn.backward(), the gradients will be accumulated" \
                  "from all loss_- fn.backward() calls and it will lead to the gradient explosion," \
                  "which fails the training."
        if gradients_not_cleared > 0:
            name_smell = "gradients_not_cleared_before_backward_propagation"
            to_return = [filename, function_name, gradients_not_cleared, name_smell, message]
            return to_return
        return []
    return []



def tensor_array_not_used(libraries, filename, fun_node):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'tensorflow' in x]:
        function_name = fun_node.name
        function_body = ast.unparse(fun_node.body).strip()
        number_of_apply = 0
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "constant":
                        if len(node.args) >= 1:
                            parameter = ast.unparse(node.args[0])
                            for arg_node in node.args:
                                if isinstance(arg_node, ast.List):
                                    number_of_apply += 1
        if number_of_apply > 0:
            message = "If the developer initializes an array using tf.constant() and tries to assign a new value to " \
                      "it in the loop to keep it growing, the code will run into an error." \
                      "Using tf.TensorArray() for growing array in the loop is a better solution for this kind of " \
                      "problem in TensorFlow 2."
            name_smell = "tensor_array_not_used"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return


def pytorch_call_method_misused(libraries, filename, node):
    if [x for x in libraries if x in test_libraries]:
        return []
    if [x for x in libraries if 'torch' in x]:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        lines = function_body.split('\n')
        number_of_forward = 0
        for line in lines:
            if ".forward(" in line:
                number_of_forward += 1
        if number_of_forward > 0:
            message = "is recommended to use self.net()"
            name_smell ="pytorch_call_method_misused"
            to_return = [filename, function_name, number_of_forward, name_smell, message]
            return to_return
        return []
    return []