"""Example of using worlds with just an integer for the state of the world"""

from dataclasses import dataclass, field, replace
from functools import partial, wraps
from itertools import islice
from typing import TypeVar, Optional

import click
import py_trees

from social_norms_trees.chat import (
    World,
    update_behavior,
    main,
)

from pprint import pformat


@dataclass
class BehaviorTreeWorld(World):
    tree: py_trees.behaviour.Behaviour = field(
        default_factory=py_trees.behaviours.Dummy
    )


def print_world(world: BehaviorTreeWorld):
    tree_display = py_trees.display.unicode_tree(world.tree)
    print(f"{pformat(world)}\n\ntree:\n{tree_display}")


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


def format_tree_with_indices(tree: py_trees.behaviour.Behaviour):
    """
    Examples:
        >>> print(format_tree_with_indices(py_trees.behaviours.Dummy()))
        0: --> Dummy
    """

    index_strings = [str(i) for i, _ in enumerate_nodes(tree)]
    max_len = max([len(s) for s in index_strings])
    padded_index_strings = [s.rjust(max_len) for s in index_strings]

    tree_representation = py_trees.display.unicode_tree(tree)
    tree_representation_lines = tree_representation.split("\n")
    enumerated_tree_representation_lines = [
        f"{i}: {t}" for i, t in zip(padded_index_strings, tree_representation_lines)
    ]

    output = "\n".join(enumerated_tree_representation_lines)
    return output


def say(message):
    print(message)


def add_child(
    tree: T,
    parent: Optional[py_trees.composites.Composite] = None,
    child: Optional[py_trees.behaviour.Behaviour] = None,
) -> T:
    if parent is None:
        parent_index = click.prompt(
            text=f"{format_tree_with_indices(tree)}\n"
            f"Which parent node do you want to add the child to?",
            type=int,
        )
        parent = next(islice(iterate_nodes(tree), parent_index, parent_index + 1))
    if child is None:
        child_key = click.prompt(
            text="What should the child do?", type=click.Choice(["say something"])
        )
        match child_key:
            case "say something":
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


if __name__ == "__main__":

    # main(world_)
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

    print(py_trees.display.ascii_tree(tree))
    print(format_tree_with_indices(tree))
    add_child(tree)
    print(format_tree_with_indices(tree))
    pass

    world_ = BehaviorTreeWorld(
        behavior=[print_world, update_behavior, add_child],
        available_behaviors=[print_world, add_child],
    )
    print_world(world_)
