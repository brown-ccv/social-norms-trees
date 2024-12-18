from social_norms_trees.custom_node_library import CustomBehavior, CustomSequence


def serialize_tree(tree, include_children=True):
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
    if include_children and tree.children:
        data["children"] = [serialize_tree(child) for child in tree.children]

    return data


def deserialize_library_element(description: dict):
    """
    Examples:
        >>> s = deserialize_library_element({"type": "Sequence", "name": "Sequence 0", "id": "s0"})
        >>> s
        <social_norms_trees.custom_node_library.CustomSequence object at 0x...>

        >>> s.id_
        's0'

        >>> s.name
        'Sequence 0'

        >>> s.children
        []

        TODO: Implement selectors
        >>> deserialize_library_element({"type": "Selector", "name": "Selector 0", "id": "s0"})
        Traceback (most recent call last):
        ...
        NotImplementedError: node_type=Selector is not implemented

        >>> b = deserialize_library_element({"type": "Behavior", "name": "Behavior 0", "id": "b0"})
        >>> b
        <social_norms_trees.custom_node_library.CustomBehavior object at 0x...>

        >>> b.id_
        'b0'

        >>> b.name
        'Behavior 0'


    """
    assert isinstance(description["type"], str), (
        f"\nThere was an invalid configuration detected in the inputted behavior tree: "
        f"Invalid type for node attribute 'type' found for node '{description['name']}'. "
        f"Please ensure that the 'name' attribute is a string."
    )

    node_type = description["type"]
    assert node_type in {"Sequence", "Selector", "Behavior"}, (
        f"\nThere was an invalid configuration detected in the inputted behavior tree: "
        f"Invalid node type '{node_type}' found for node '{description['name']}'. "
        f"Please ensure that all node types are correct and supported."
    )

    if node_type == "Sequence":
        if "children" in description.keys():
            children = [
                deserialize_library_element(child) for child in description["children"]
            ]
        else:
            children = []

        node = CustomSequence(
            name=description["name"],
            id_=description["id"],
            display_name=description["name"],
            children=children,
        )

    elif node_type == "Behavior":
        assert "children" not in description or len(description["children"]) == 0, (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Children were detected for Behavior type node '{description['name']}': "
            f"Behavior nodes should not have any children. Please check the structure of your behavior tree."
        )

        node = CustomBehavior(
            name=description["name"],
            id_=description["id"],
            display_name=description["name"],
        )

    else:
        msg = "node_type=%s is not implemented" % node_type
        raise NotImplementedError(msg)

    return node


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
                    name=behavior["name"],
                    id_=behavior["id"],
                    display_name=behavior["name"],
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
                    name=behavior["name"],
                    id_=behavior["id"],
                    display_name=behavior["name"],
                )
            else:
                raise ValueError(
                    f"Behavior {node['name']} not found in behavior library"
                )

    return deserialize_node(tree)
