import ast
import re


def Chain_Indexing(libraries, filename, node):
    if "pandas" in libraries:
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


def dataframe_conversion_api_misused(libraries, filename, node):
    if "pandas" in libraries:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        number_of_apply = function_body.count(".values(")
        message = "Please consider to use numpy instead values to convert dataframe. The function 'values' is deprecated." \
                  "The value return of this function is unclear."
        if number_of_apply > 0:
            name_smell = "dataframe_conversion_api_misused"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return
        return []
    return []


def matrix_multiplication_api_misused(libraries, filename, node):
    if "numpy" in libraries:
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
    if "pytorch" in libraries:
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


def tensor_array_not_used(libraries, filename, node):
    if "tensorflow" in libraries:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        lines = function_body.split('\n')
        tensor_array = False
        number_of_apply = 0
        for line in lines:
            if "tf.constant" in line:
                parameter = line.split("(")[1].split(")")[0]
                if "[" in parameter:
                    number_of_apply += 1
        if number_of_apply > 0:
            message = "If the developer initializes an array using tf.constant() and tries to assign a new value to " \
                      "it in the loop to keep it growing, the code will run into an error." \
                      "Using tf.TensorArray() for growing array in the loop is a better solution for this kind of " \
                      "problem in TensorFlow 2. "
            name_smell = "tensor_array_not_used"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return
        return []
    return []


def pytorch_call_method_misused(libraries, filename, node):
    if "pytorch" in libraries:
        function_name = node.name
        function_body = ast.unparse(node.body).strip()
        lines = function_body.split('\n')
        number_of_forward = 0
        for line in lines:
            if "net.forward(" in line:
                number_of_forward += 1
        if number_of_forward > 0:
            message = "is recommended to use self.net()"
            name_smell ="pytorch_call_method_misused"
            to_return = [filename, function_name, number_of_forward, name_smell, message]
            return to_return
        return []
    return []
