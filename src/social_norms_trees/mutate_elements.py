from collections import namedtuple
import inspect
from functools import wraps
import logging
import sys
from types import GenericAlias
from typing import Callable, List, Tuple, TypeVar, Union, Dict

import click
import py_trees

from social_norms_trees.mutate_tree import (
    prompt_identify_node,
    prompt_identify_parent_node,
    prompt_identify_child_index,
    prompt_identify_library_node,
)

_logger = logging.getLogger(__name__)

# =============================================================================
# Argument types
# =============================================================================

ExistingNode = TypeVar("ExistingNode", bound=py_trees.behaviour.Behaviour)
NewNode = TypeVar("NewNode", bound=py_trees.behaviour.Behaviour)
CompositeIndex = TypeVar(
    "CompositeIndex", bound=Tuple[py_trees.composites.Composite, int]
)

# =============================================================================
# Atomic operations
# =============================================================================

# The very top line of each operation's docstring is used as the
# description of the operation in the UI, so it's required.
# The argument annotations are vital, because they tell the UI which prompt
# to use.


def remove(node: ExistingNode) -> ExistingNode:
    """Remove a node.

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success(),
        ...    failure := py_trees.behaviours.Failure()])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> removed = remove(failure)
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

    """
    if node.parent is None:
        msg = (
            f"%s's parent is None, so we can't remove it. We can't remove the root node."
            % (node)
        )
        raise ValueError(msg)
    elif isinstance(node.parent, py_trees.composites.Composite):
        node.parent.remove_child(node)
    else:
        raise NotImplementedError()
    return node


def insert(node: NewNode, where: CompositeIndex) -> None:
    """Insert a new node.

    Examples:

        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success()
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

        >>> insert(py_trees.behaviours.Failure(), (tree, 1))
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> insert(py_trees.behaviours.Dummy(), (tree, 0))
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Dummy
            --> Success
            --> Failure

    """
    parent, index = where
    parent.insert_child(node, index)
    return


def move(
    node: ExistingNode,
    where: CompositeIndex,
) -> None:
    """Move a node.

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...     failure_node := py_trees.behaviours.Failure(),
        ...     success_node := py_trees.behaviours.Success(),
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Failure
            --> Success
        >>> move(failure_node, (tree, 1))
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

            >>> move(failure_node, (tree, 1))
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

    """
    parent, index = where
    insert(remove(node), (parent, index))
    return


def exchange(
    node0: ExistingNode,
    node1: ExistingNode,
) -> None:
    """Exchange two nodes.

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...     s := py_trees.behaviours.Success(),
        ...     f := py_trees.behaviours.Failure(),
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> exchange(s, f)
        >>> print(py_trees.display.ascii_tree(tree))
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

        >>> exchange(a, c)
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] C
            [-] B
                --> Success
                [-] A
                    --> Dummy

        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...     py_trees.composites.Sequence("1", False, children=[
        ...         a := py_trees.behaviours.Dummy("A")
        ...     ]),
        ...     py_trees.composites.Sequence("2", False, children=[
        ...         b := py_trees.behaviours.Dummy("B")
        ...     ])
        ... ])

        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] 1
                --> A
            [-] 2
                --> B
        >>> exchange(a, b)
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] 1
                --> B
            [-] 2
                --> A
    """

    node0_parent, node0_index = node0.parent, node0.parent.children.index(
        node0)
    node1_parent, node1_index = node1.parent, node1.parent.children.index(
        node1)

    move(node0, (node1_parent, node1_index))
    move(node1, (node0_parent, node0_index))

    return


# =============================================================================
# User Interface
# =============================================================================

# Wrapper functions for the atomic operations which give them a UI.

MutationResult = namedtuple(
    "MutationResult", ["result", "tree", "function", "kwargs"])


def mutate_chooser(*fs: Union[Callable], message="Which action?"):
    """Prompt the user to choose one of the functions f.

    Returns the wrapped version of the function.
    """
    n_fs = len(fs)
    docstring_summaries = [f_.__doc__.split("\n")[0] for f_ in fs]
    text = (
        "\n".join(
            [
                f"{i}: {docstring_summary}"
                for i, docstring_summary in enumerate(docstring_summaries)
            ]
        )
        + f"\n{message}"
    )
    i = click.prompt(text=text, type=click.IntRange(0, n_fs))
    f = mutate_ui(fs[i])

    return f


def mutate_ui(
    f,
) -> Callable[[py_trees.behaviour.Behaviour, List[py_trees.behaviour.Behaviour]], Dict]:
    """Factory function for a tree mutator UI.

    This creates a version of the atomic function `f`
    which prompts the user for the appropriate arguments 
    based on `f`'s type annotations.
    """

    signature = inspect.signature(f)

    @wraps(f)
    def f_inner(tree, library):
        kwargs = {}
        for parameter_name in signature.parameters.keys():
            annotation = signature.parameters[parameter_name].annotation
            _logger.debug(f"getting arguments for {annotation=}")
            value = prompt_get_mutate_arguments(annotation, tree, library)
            kwargs[parameter_name] = value
        inner_result = f(**kwargs)
        return_value = MutationResult(
            result=inner_result, tree=tree, function=f, kwargs=kwargs
        )
        return return_value

    return f_inner


def prompt_get_mutate_arguments(annotation: GenericAlias, tree, library):
    """Prompt the user to specify nodes and positions in the tree."""
    annotation_ = str(annotation)
    assert isinstance(annotation_, str)

    if annotation_ == str(inspect.Parameter.empty):
        _logger.debug("in empty")
        msg = "Can't work out what argument %s should be" % annotation
        raise ValueError(msg)
    elif annotation_ == str(ExistingNode):
        _logger.debug("in ExistingNode")
        node = prompt_identify_node(tree)
        return node
    elif annotation_ == str(CompositeIndex):
        _logger.debug("in CompositeIndex")
        composite_node = prompt_identify_parent_node(
            tree, message="Which parent?")
        index = prompt_identify_child_index(composite_node)
        return composite_node, index
    elif annotation_ == str(NewNode):
        _logger.debug("in NewNode")
        new_node_index = prompt_identify_library_node(
            library, "Which node from the library?"
        )
        new_node = library[new_node_index]
        return new_node
    else:
        _logger.debug("in 'else'")
        msg = "Can't work out what to do with %s" % annotation
        raise NotImplementedError(msg)


# =============================================================================
# Utility functions
# =============================================================================


class QuitException(Exception):
    pass


def quit():
    """Finish the experiment."""
    raise QuitException("User quit the experiment.")


# =============================================================================
# Main Loop
# =============================================================================

def load_experiment():
    """Placeholder function for loading a tree and library (should come from a file)."""
    tree = py_trees.composites.Sequence(
        "S0",
        False,
        children=[
            py_trees.behaviours.Dummy("A"),
            py_trees.composites.Sequence(
                "S1",
                memory=False,
                children=[
                    py_trees.behaviours.Dummy("B"),
                    py_trees.behaviours.Dummy("C"),
                    py_trees.behaviours.Dummy("D"),
                ],
            ),
            py_trees.composites.Selector(
                "S2",
                memory=False,
                children=[
                    py_trees.behaviours.Dummy("E"),
                    py_trees.behaviours.Dummy("F"),
                    py_trees.behaviours.Failure(),
                ],
            ),
            py_trees.behaviours.Success(),
        ],
    )
    library = [py_trees.behaviours.Success(
    ), py_trees.behaviours.Failure()]
    return tree, library


def save_results(tree, protocol):
    _logger.info("saving results")
    print(f"protocol: {protocol}")
    print(f"tree:\n{py_trees.display.unicode_tree(tree)}")


def main():
    logging.basicConfig(level=logging.DEBUG)
    tree, library = load_experiment()
    protocol = []
    exit_code = None

    try:
        print(py_trees.display.ascii_tree(tree))

        # The main loop of the experiment
        while f := mutate_chooser(insert, move, exchange, remove, quit):
            try:
                results = f(tree, library)
                _logger.debug(results)
                protocol.append(results)
                print(py_trees.display.ascii_tree(tree))

            # If we have any errors raised by the function, like wrong values,
            # we don't want to crash.
            except (ValueError, IndexError, NotImplementedError) as e:
                _logger.error(f"\n{e}")
                continue

    # If the user calls the "quit" function, then we want to exit
    except QuitException as e:
        _logger.debug(e)
        exit_code = 0

    # If the user does a keyboard interrupt, then we want to exit
    except click.exceptions.Abort:
        print("\n")
        _logger.error("Program aborted.")
        exit_code = 1

    # Save the results
    finally:
        _logger.debug("finally")
        save_results(tree, protocol)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
