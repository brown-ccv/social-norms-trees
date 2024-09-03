import py_trees


def serialize_tree(tree):
    def serialize_node(node):
        data = {
            "type": node.__class__.__name__,
            "name": node.name,
            "children": [serialize_node(child) for child in node.children],
        }
        return data

    return serialize_node(tree)

def deserialize_tree(tree):
    def deserialize_node(node):
        node_type = node['type']
        children = [deserialize_node(child) for child in node['children']]
        
        if node_type == 'Sequence':
            return py_trees.composites.Sequence(node['name'], False, children=children)
        elif node_type == 'Dummy':
            return py_trees.behaviours.Dummy(node['name'])
        elif node_type == 'Success':
            return py_trees.behaviours.Success(node['name'])
        elif node_type == 'Failure':
            return py_trees.behaviours.Failure(node['name'])
        elif node_type == 'Running':
            return py_trees.behaviours.Running(node['name'])
     
    return deserialize_node(tree)