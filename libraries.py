import ast


def extract_libraries(tree):
    """
    Given a tree obtained from `ast.parse` command, extract a list of libraries used in the tree.
    """
    libraries = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                libraries.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            libraries.append(node.module)
    return libraries