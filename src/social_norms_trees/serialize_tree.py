import py_trees
from social_norms_trees.custom_node_library import CustomBehavior


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
        node_type = node["type"]
        children = [deserialize_node(child) for child in node["children"]]

        if node_type == "Sequence":
            return py_trees.composites.Sequence(node["name"], False, children=children)
        elif node_type == "Behavior":
            behavior = behavior_library.get_behavior_by_nickname(node["name"])
            if behavior:
                return CustomBehavior(
                    name=behavior["nickname"],
                    id_=behavior["id"],
                    nickname=behavior["nickname"],
                )
            else:
                raise ValueError(
                    f"Behavior {node['name']} not found in behavior library"
                )

    return deserialize_node(tree)
