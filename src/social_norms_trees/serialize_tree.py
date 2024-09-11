import py_trees
from social_norms_trees.custom_node_library import CustomAction


def serialize_tree(tree):
    def serialize_node(node):
        data = {
            "type": node.__class__.__name__,
            "name": node.name,
            "children": [serialize_node(child) for child in node.children],
        }
        return data

    return serialize_node(tree)

def deserialize_tree(tree, action_library):
    def deserialize_node(node):
        node_type = node['type']
        children = [deserialize_node(child) for child in node['children']]

        if node_type == 'Sequence':
            return py_trees.composites.Sequence(node['name'], False, children=children)
        elif node_type == 'Action':
            action = action_library.get_action_by_nickname(node['name'])
            if action:
                return CustomAction(
                    name=action['nickname'],
                    id=action['id'],
                    nickname=action['nickname']
                )
            else:
                raise ValueError(f"Action {node['name']} not found in action library")
            
    return deserialize_node(tree)