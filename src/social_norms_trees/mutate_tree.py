"""Example of using worlds with just an integer for the state of the world"""

import warnings
from functools import partial, wraps
from itertools import islice
from typing import TypeVar, Optional, List

import click
import py_trees

from datetime import datetime

from social_norms_trees.custom_node_library import CustomBehavior, CustomSequence


T = TypeVar("T", bound=py_trees.behaviour.Behaviour)


def print_tree(tree: py_trees.behaviour.Behaviour):
    tree_display = py_trees.display.unicode_tree(tree)
    print(tree_display)


def iterate_nodes(tree: py_trees.behaviour.Behaviour):
    """

    Examples:
        >>> list(iterate_nodes(py_trees.behaviours.Dummy()))  # doctest: +ELLIPSIS
        [<py_trees.behaviours.Dummy object at 0x...>]

        >>> list(iterate_nodes(
        ...     py_trees.composites.Sequence("", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ... ])))  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [<py_trees.composites.Sequence object at 0x...>,
         <py_trees.behaviours.Dummy object at 0x...>]

        >>> list(iterate_nodes(
        ...     py_trees.composites.Sequence("", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ...         py_trees.behaviours.Dummy(),
        ...         py_trees.composites.Sequence("", False, children=[
        ...             py_trees.behaviours.Dummy(),
        ...         ]),
        ... ])))  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [<py_trees.composites.Sequence object at 0x...>,
         <py_trees.behaviours.Dummy object at 0x...>,
         <py_trees.behaviours.Dummy object at 0x...>,
         <py_trees.composites.Sequence object at 0x...>,
         <py_trees.behaviours.Dummy object at 0x...>]

    """
    yield tree
    for child in tree.children:
        yield from iterate_nodes(child)


def enumerate_nodes(tree: py_trees.behaviour.Behaviour):
    """

    Examples:
        >>> list(enumerate_nodes(py_trees.behaviours.Dummy()))  # doctest: +ELLIPSIS
        [(0, <py_trees.behaviours.Dummy object at 0x...>)]

        >>> list(enumerate_nodes(
        ...     py_trees.composites.Sequence("", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ... ])))  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [(0, <py_trees.composites.Sequence object at 0x...>),
         (1, <py_trees.behaviours.Dummy object at 0x...>)]

        >>> list(enumerate_nodes(
        ...     py_trees.composites.Sequence("s1", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ...         py_trees.behaviours.Success(),
        ...         py_trees.composites.Sequence("s2", False, children=[
        ...             py_trees.behaviours.Dummy(),
        ...         ]),
        ...         py_trees.composites.Sequence("", False, children=[
        ...             py_trees.behaviours.Failure(),
        ...             py_trees.behaviours.Periodic("p", n=1),
        ...         ]),
        ... ])))  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [(0, <py_trees.composites.Sequence object at 0x...>),
         (1, <py_trees.behaviours.Dummy object at 0x...>),
         (2, <py_trees.behaviours.Success object at 0x...>),
         (3, <py_trees.composites.Sequence object at 0x...>),
         (4, <py_trees.behaviours.Dummy object at 0x...>),
         (5, <py_trees.composites.Sequence object at 0x...>),
         (6, <py_trees.behaviours.Failure object at 0x...>),
         (7, <py_trees.behaviours.Periodic object at 0x...>)]

    """
    return enumerate(iterate_nodes(tree))


def label_tree_lines(
    tree: py_trees.behaviour.Behaviour,
    labels: List[str],
    representation=py_trees.display.unicode_tree,
) -> str:
    max_len = max([len(s) for s in labels])
    padded_labels = [s.rjust(max_len) for s in labels]

    tree_representation_lines = representation(tree).split("\n")
    enumerated_tree_representation_lines = [
        f"{i}: {t}" for i, t in zip(padded_labels, tree_representation_lines)
    ]

    output = "\n".join(enumerated_tree_representation_lines)
    return output


def format_children_with_indices(composite: py_trees.composites.Composite) -> str:
    """
    Examples:
        >>> tree = py_trees.composites.Sequence("s1", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ...         py_trees.behaviours.Success(),
        ...         py_trees.composites.Sequence("s2", False, children=[
        ...             py_trees.behaviours.Dummy(),
        ...         ]),
        ...         py_trees.composites.Sequence("", False, children=[
        ...             py_trees.behaviours.Failure(),
        ...             py_trees.behaviours.Periodic("p", n=1),
        ...         ]),
        ... ])
        >>> print(format_children_with_indices(tree))  # doctest: +NORMALIZE_WHITESPACE
        _:  [-] s1
        0:     --> Dummy
        1:     --> Success
        2:     [-] s2
        _:         --> Dummy
        3:     [-]
        _:         --> Failure
        _:         --> p
    """
    index_strings = []
    i = 0
    for b in iterate_nodes(composite):
        if b in composite.children:
            index_strings.append(str(i))
            i += 1
        else:
            index_strings.append("_")

    index_strings.append(str(i))

    output = label_tree_lines(composite, index_strings)
    return output


def format_parents_with_indices(composite: py_trees.composites.Composite) -> str:
    index_strings = []
    i = 0
    for b in iterate_nodes(composite):
        if (
            b.__class__.__name__ == "CustomSequence"
            or b.__class__.__name__ == "CustomSelector"
        ):
            index_strings.append(str(i))
        else:
            index_strings.append("_")
        i += 1

    output = label_tree_lines(composite, index_strings)
    return output


def format_tree_with_indices(
    tree: py_trees.behaviour.Behaviour,
    show_root: bool = False,
) -> tuple[str, List[str]]:
    """
    Examples:
        >>> print(format_tree_with_indices(py_trees.behaviours.Dummy()))
        0: --> Dummy

        >>> tree = py_trees.composites.Sequence("s1", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ...         py_trees.behaviours.Success(),
        ...         py_trees.composites.Sequence("s2", False, children=[
        ...             py_trees.behaviours.Dummy(),
        ...         ]),
        ...         py_trees.composites.Sequence("", False, children=[
        ...             py_trees.behaviours.Failure(),
        ...             py_trees.behaviours.Periodic("p", n=1),
        ...         ]),
        ... ])
        >>> print(format_tree_with_indices(tree))  # doctest: +NORMALIZE_WHITESPACE
        0: [-] s1
        1:     --> Dummy
        2:     --> Success
        3:     [-] s2
        4:         --> Dummy
        5:     [-]
        6:         --> Failure
        7:         --> p

    """

    index_strings = []
    index = 0
    for i, node in enumerate_nodes(tree):
        if i == 0 and not show_root:
            index_strings.append("_")
        else:
            index_strings.append(str(index))
        index += 1
    output = label_tree_lines(tree, index_strings)

    return output, index_strings[1:]


def say(message):
    print(message)


def prompt_identify_node(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which node?",
    display_nodes: bool = True,
    show_root: bool = False,
) -> py_trees.behaviour.Behaviour:
    node_index = prompt_identify_tree_iterator_index(
        tree=tree, message=message, display_nodes=display_nodes, show_root=show_root
    )
    node = next(islice(iterate_nodes(tree), node_index, node_index + 1))
    return node


def prompt_identify_parent_node(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which position?",
    display_nodes: bool = True,
) -> int:
    if display_nodes:
        text = f"{format_parents_with_indices(tree)}\n{message}"
    else:
        text = f"{message}"
    node_index = click.prompt(
        text=text,
        type=int,
    )

    node = next(islice(iterate_nodes(tree), node_index, node_index + 1))
    return node


def prompt_identify_tree_iterator_index(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which position?",
    display_nodes: bool = True,
    show_root: bool = False,
) -> int:
    if display_nodes:
        format_tree_text, index_options = format_tree_with_indices(tree, show_root)
        text = f"{format_tree_text}\n{message}"
    else:
        _, index_options = format_tree_with_indices(tree, show_root)
        text = f"{message}"
    node_index = click.prompt(
        text=text,
        type=click.Choice(index_options, case_sensitive=False),
        show_choices=False,
    )
    return int(node_index)


def prompt_identify_child_index(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which position?",
    display_nodes: bool = True,
) -> int:
    if display_nodes:
        text = f"{format_children_with_indices(tree)}\n{message}"
    else:
        text = f"{message}"
    node_index = click.prompt(
        text=text,
        type=int,
    )
    return node_index


def add_child(
    tree: T,
    parent: Optional[py_trees.composites.Composite] = None,
    child: Optional[py_trees.behaviour.Behaviour] = None,
) -> T:
    """Add a behaviour to the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]

        >>> print(py_trees.display.ascii_tree(add_child(tree, py_trees.behaviours.Success())))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

    """
    if parent is None:
        parent = prompt_identify_node(
            tree, f"Which parent node do you want to add the child to?"
        )
    if child is None:
        child_key = click.prompt(
            text="What should the child do?", type=click.Choice(["say"])
        )
        match child_key:
            case "say":
                message = click.prompt(text="What should it say?", type=str)

                child_function = wraps(say)(partial(say, message))
                child_type = py_trees.meta.create_behaviour_from_function(
                    child_function
                )
                child = child_type()
            case _:
                raise NotImplementedError()
    parent.add_child(child)
    return tree


def remove_node(tree: T, node: Optional[py_trees.behaviour.Behaviour] = None) -> T:
    """Remove a behaviour from the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success(),
        ...    failure_node := py_trees.behaviours.Failure()])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> print(py_trees.display.ascii_tree(remove_node(tree, failure_node)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

    """
    if node is None:
        node = prompt_identify_node(tree, f"Which node do you want to remove?")
    parent_node = node.parent
    if parent_node is None:
        warnings.warn(
            f"{node}'s parent is None, so we can't remove it. You can't remove the root node."
        )
        action_log = {}
        return (tree,)
    elif isinstance(parent_node, py_trees.composites.Composite):
        parent_node.remove_child(node)
        action_log = {
            "type": "remove_node",
            "nodes": [
                {"id_": node.id_, "display_name": node.display_name},
            ],
            "timestamp": datetime.now().isoformat(),
        }
    else:
        raise NotImplementedError()

    return tree, action_log


def move_node(
    tree: T,
    node: Optional[py_trees.behaviour.Behaviour] = None,
    new_parent: Optional[py_trees.behaviour.Behaviour] = None,
    index: int = None,
    internal_call: bool = False,
) -> T:
    """Exchange two behaviours in the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[])

    """

    if node is None:
        node = prompt_identify_node(tree, f"Which node do you want to move?")
    if new_parent is None:
        new_parent = prompt_identify_parent_node(
            tree, f"What should its parent be?", display_nodes=True
        )
    if index is None:
        index = prompt_identify_child_index(new_parent)

    assert isinstance(new_parent, py_trees.composites.Composite)
    assert isinstance(node.parent, py_trees.composites.Composite)

    # old_parent = node.parent.name
    node.parent.remove_child(node)
    new_parent.insert_child(node, index)

    if not internal_call:
        action_log = {
            "type": "move_node",
            "nodes": [
                {
                    "id": node.id_,
                    "display_name": node.display_name,
                },
            ],
            "timestamp": datetime.now().isoformat(),
        }
        return tree, action_log

    return tree


def exchange_nodes(
    tree: T,
    node0: Optional[py_trees.behaviour.Behaviour] = None,
    node1: Optional[py_trees.behaviour.Behaviour] = None,
) -> T:
    """Exchange two behaviours in the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...     s:=py_trees.behaviours.Success(),
        ...     f:=py_trees.behaviours.Failure(),
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> print(py_trees.display.ascii_tree(exchange_nodes(tree, s, f)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Failure
            --> Success

        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...     a:= py_trees.composites.Sequence("A", False, children=[
        ...         py_trees.behaviours.Dummy()
        ...     ]),
        ...     py_trees.composites.Sequence("B", False, children=[
        ...         py_trees.behaviours.Success(),
        ...         c := py_trees.composites.Sequence("C", False, children=[])
        ...     ])
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] A
                --> Dummy
            [-] B
                --> Success
                [-] C
        >>> print(py_trees.display.ascii_tree(exchange_nodes(tree, a, c)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] C
            [-] B
                --> Success
                [-] A
                    --> Dummy
    """

    if node0 is None:
        node0 = prompt_identify_node(tree, f"Which node do you want to switch?")
    if node1 is None:
        node1 = prompt_identify_node(
            tree, f"Which node do you want to switch?", display_nodes=False
        )

    node0_parent, node0_index = node0.parent, node0.parent.children.index(node0)
    node1_parent, node1_index = node1.parent, node1.parent.children.index(node1)

    tree = move_node(tree, node0, node1_parent, node1_index, True)
    tree = move_node(tree, node1, node0_parent, node0_index, True)

    nodes = []
    if node0.__class__.__name__ != "CustomBehavior":
        nodes.append(
            {
                "display_name": node0.name,
            }
        )
    else:
        nodes.append({"id": node0.id_, "display_name": node0.display_name})

    if node1.__class__.__name__ != "CustomBehavior":
        nodes.append(
            {
                "display_name": node1.display_name,
            }
        )
    else:
        nodes.append({"id": node1.id_, "display_name": node1.display_name})

    action_log = {
        "type": "exchange_nodes",
        "nodes": nodes,
        "timestamp": datetime.now().isoformat(),
    }
    return tree, action_log


def prompt_select_node(behavior_library, text):

    for idx, tree_name in enumerate(behavior_library.behaviors.keys(), 1):
        print(f"{idx}. {tree_name}")
    for idx, tree_name in enumerate(
        behavior_library.behavior_from_display_name.keys(), 1
    ):
        print(f"{idx}. {tree_name}")

    node_index = click.prompt(
        text=text,
        type=int,
    )
    choices = [str(i + 1) for i in range(len(behavior_library.behaviors))]
    node_index = click.prompt(text=text, type=click.Choice(choices), show_choices=False)

    node_key = list(behavior_library.behavior_from_display_name.keys())[node_index - 1]

    return behavior_library.behavior_from_display_name[node_key]


def add_node(
    tree: T,
    behavior_library: object,
) -> T:
    """Exchange two behaviours in the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[])

    """

    behavior = prompt_select_node(
        behavior_library, f"Which behavior do you want to add?"
    )

    if behavior["type"] == "Behavior":
        new_node = CustomBehavior(
            name=behavior["display_name"],
            id_=behavior["id"],
            display_name=behavior["display_name"],
        )

    elif behavior["type"] == "Sequence":
        new_node = CustomSequence(
            name=behavior["display_name"],
            id_=behavior["id"],
            display_name=behavior["display_name"],
        )

    new_parent = prompt_identify_parent_node(
        tree, f"What should its parent be?", display_nodes=True
    )

    index = prompt_identify_child_index(new_parent)

    assert isinstance(new_parent, py_trees.composites.Composite)

    new_parent.insert_child(new_node, index)

    action_log = {
        "type": "add_node",
        "node": {"id": new_node.id_, "display_name": new_node.display_name},
        "timestamp": datetime.now().isoformat(),
    }

    return tree, action_log
