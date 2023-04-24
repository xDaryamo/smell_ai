import ast

def extract_libraries(tree):
    """
    Given a tree obtained from ast.parse command, extract a list of libraries used in the tree.
    """
    libraries = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    libraries.append(alias.name + ' as ' + alias.asname)
                else:
                    libraries.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.module != "*":
                    module_name = node.module
                    if node.asname:
                        module_name += ' as ' + node.asname
                    for alias in node.names:
                        if alias.asname:
                            libraries.append(module_name + '.' + alias.name + ' as ' + alias.asname)
                        else:
                            libraries.append(module_name + '.' + alias.name)
                else:
                    libraries.append(node.module)

    return set(libraries)
