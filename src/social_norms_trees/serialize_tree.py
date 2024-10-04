import py_trees
from social_norms_trees.custom_node_library import CustomBehavior, CustomSequence


def serialize_tree(tree):
    def serialize_node(node):
        data = {
            "type": node.__class__.__name__,
            "name": node.name,
            "children": [serialize_node(child) for child in node.children],
        }
        return data

    return serialize_node(tree)

def deserialize_tree(tree, behavior_library):
    def deserialize_node(node):
        node_type = node['type']
        children = [deserialize_node(child) for child in node['children']]

        behavior = behavior_library.behavior_from_display_name[node['name']]

        if node_type == 'Sequence':
            if behavior:
                return CustomSequence(
                    name=behavior['display_name'],
                    id_=behavior['id'],
                    display_name=behavior['display_name'],
                    children=children
                )
            else:
                raise ValueError(f"Behavior {node['name']} not found in behavior library")
            
        elif node_type == 'Behavior':
            if behavior:
                return CustomBehavior(
                    name=behavior['display_name'],
                    id_=behavior['id'],
                    display_name=behavior['display_name']
                )
            else:
                raise ValueError(f"Behavior {node['name']} not found in behavior library")
            
    return deserialize_node(tree)