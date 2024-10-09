import py_trees
from social_norms_trees.custom_node_library import CustomBehavior, CustomSequence


def serialize_tree(tree):
    """
    Examples:
        >>> from py_trees.behaviours import Dummy, Success, Failure
        >>> from py_trees.composites import Sequence, Selector

        >>> serialize_tree(Dummy())
        {'type': 'Dummy', 'name': 'Dummy'}

        >>> serialize_tree(Success())
        {'type': 'Success', 'name': 'Success'}

        >>> serialize_tree(Failure())
        {'type': 'Failure', 'name': 'Failure'}

        >>> serialize_tree(Sequence("root", True, children=[Dummy()]))
        {'type': 'Sequence', 'name': 'root', 'children': [{'type': 'Dummy', 'name': 'Dummy'}]}

        >>> serialize_tree(CustomBehavior("behavior", "theid", "display behavior"))
        {'type': 'CustomBehavior', 'name': 'behavior', 'display_name': 'display behavior', 'id_': 'theid'}

        >>> serialize_tree(CustomSequence("root", "theid", "display root", children=[Dummy()]))
        {'type': 'CustomSequence', 'name': 'root', 'display_name': 'display root', 'id_': 'theid', 'children': [{'type': 'Dummy', 'name': 'Dummy'}]}
    """

    data = {
        "type": tree.__class__.__name__,
        "name": tree.name,
    }
    if hasattr(tree, "display_name"):
        data["display_name"] = tree.display_name
    if hasattr(tree, "id_"):
        data["id_"] = tree.id_
    if tree.children:
        data["children"] = [serialize_tree(child) for child in tree.children]

    return data


def deserialize_tree(tree, behavior_library):
    def deserialize_node(node):
        assert type(node["type"] == str), (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Invalid type for node attribute 'type' found for node '{node['name']}'. "
            f"Please ensure that the 'name' attribute is a string."
        )
        assert type(node["name"] == str), (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Invalid type for node attribute 'name' found for node '{node['name']}'. "
            f"Please ensure that the 'name' attribute is a string."
        )

        node_type = node["type"]
        assert node_type in ["Sequence", "Selector", "Behavior"], (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Invalid node type '{node_type}' found for node '{node['name']}'. "
            f"Please ensure that all node types are correct and supported."
        )

        behavior = behavior_library.behavior_from_display_name[node["name"]]

        if node_type == "Sequence":
            children = [deserialize_node(child) for child in node["children"]]

            if behavior:
                return CustomSequence(
                    name=behavior["display_name"],
                    id_=behavior["id"],
                    display_name=behavior["display_name"],
                    children=children,
                )
            else:
                raise ValueError(
                    f"Behavior {node['name']} not found in behavior library"
                )

        # TODO: node type Selector

        elif node_type == "Behavior":
            assert "children" not in node or len(node["children"]) == 0, (
                f"\nThere was an invalid configuration detected in the inputted behavior tree: "
                f"Children were detected for Behavior type node '{node['name']}': "
                f"Behavior nodes should not have any children. Please check the structure of your behavior tree."
            )

            if behavior:
                return CustomBehavior(
                    name=behavior["display_name"],
                    id_=behavior["id"],
                    display_name=behavior["display_name"],
                )
            else:
                raise ValueError(
                    f"Behavior {node['name']} not found in behavior library"
                )

    return deserialize_node(tree)
