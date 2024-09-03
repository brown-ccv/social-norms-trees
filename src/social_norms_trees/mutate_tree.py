"""Example of using worlds with just an integer for the state of the world"""

import warnings
from functools import partial, wraps
from itertools import islice
from typing import TypeVar, Optional, List

import click
import py_trees

from serialize_tree import serialize_tree, deserialize_tree
import json

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

    output = label_tree_lines(composite, index_strings)
    return output


def format_tree_with_indices(tree: py_trees.behaviour.Behaviour, mode: str = "all") -> str:
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
        if mode == "children" and node.children:
            # Do not number parent nodes in 'children' mode
            index_strings.append('_')
        elif mode == "parents" and not node.children:
            # Do not number child nodes in 'parents' mode
            index_strings.append('_')
        else:
            # Number all nodes in 'all' mode
            index_strings.append(str(index))
        index += 1


    output = label_tree_lines(tree, index_strings)

    return output


def say(message):
    print(message)


def prompt_identify_node(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which node?",
    display_nodes: bool = True,
    mode: str = "all"
) -> py_trees.behaviour.Behaviour:
    node_index = prompt_identify_tree_iterator_index(
        tree=tree, message=message, display_nodes=display_nodes, mode=mode
    )
    node = next(islice(iterate_nodes(tree), node_index, node_index + 1))
    return node


def prompt_identify_tree_iterator_index(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which position?",
    display_nodes: bool = True,
    mode: str = "all"
) -> int:
    if display_nodes:
        text = f"{format_tree_with_indices(tree, mode)}\n{message}"
    else:
        text = f"{message}"
    node_index = click.prompt(
        text=text,
        type=int,
    )
    return node_index


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
        node = prompt_identify_node(tree, f"Which node do you want to remove?", True, "children")
    parent_node = node.parent
    if parent_node is None:
        warnings.warn(
            f"{node}'s parent is None, so we can't remove it. You can't remove the root node."
        )
        return tree
    elif isinstance(parent_node, py_trees.composites.Composite):
        parent_node.remove_child(node)
    else:
        raise NotImplementedError()
    return tree


def move_node(
    tree: T,
    node: Optional[py_trees.behaviour.Behaviour] = None,
    new_parent: Optional[py_trees.behaviour.Behaviour] = None,
    index: int = None,
) -> T:
    """Exchange two behaviours in the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[])

    """

    if node is None:
        node = prompt_identify_node(tree, f"Which node do you want to move?")
    if new_parent is None:
        new_parent = prompt_identify_node(
            tree, f"What should its parent be?", display_nodes=False
        )
    if index is None:
        index = prompt_identify_child_index(new_parent)

    assert isinstance(new_parent, py_trees.composites.Composite)
    assert isinstance(node.parent, py_trees.composites.Composite)

    node.parent.remove_child(node)
    new_parent.insert_child(node, index)

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

    tree = move_node(tree, node0, node1_parent, node1_index)
    tree = move_node(tree, node1, node0_parent, node0_index)

    return tree



def run_experiment(participant_id, round_number, experiment_tree):
    move_node(experiment_tree)

    serialized_tree = serialize_tree(experiment_tree)
    if participant_id not in tree_history:
        tree_history[participant_id] = {}

    tree_history[participant_id][round_number] = serialized_tree



if __name__ == "__main__":


    tree = py_trees.composites.Sequence(
        "",
        False,
        children=[
            py_trees.behaviours.Dummy(),
            py_trees.behaviours.Dummy(),
            py_trees.composites.Sequence(
                "",
                False,
                children=[
                    py_trees.behaviours.Success(),
                    py_trees.behaviours.Dummy(),
                ],
            ),
            py_trees.composites.Sequence(
                "",
                False,
                children=[
                    py_trees.behaviours.Dummy(),
                    py_trees.behaviours.Failure(),
                    py_trees.behaviours.Dummy(),
                    py_trees.behaviours.Running(),
                ],
            ),
        ],
    )

    tree_history = {
        "original_tree": serialize_tree(tree)
    }


    for x in range(2):
        print("_____________________\n")

        original_tree = deserialize_tree(tree_history["original_tree"])

        run_experiment("1234", x+1, original_tree)
    
    print("\n EXPERIMENT DONE \n")

    print(json.dumps(tree_history, indent=4))
