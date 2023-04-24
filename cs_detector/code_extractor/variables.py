import re
def get_variable_def(line):
    pattern = r'(\w)+(\[.*\])+\s*=\s*(\w*)'
    if re.match(pattern, line):
        # get the variable name
        variable = line.split('=')[0].strip().split('[')[0].strip()
        return variable
    return None

def get_all_set_variables(lines):
    variables = []
    for line in lines:
        variable = get_variable_def(line)
        if variable:
            variables.append(variable)
    return set(variables)
