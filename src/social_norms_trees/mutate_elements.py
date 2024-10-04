from collections import namedtuple
import inspect
from functools import wraps
from itertools import islice
import logging
import sys
from types import GenericAlias
from typing import Callable, List, Tuple, TypeVar, Union, Dict

import click
import py_trees

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
# Node and Position Selectors
# =============================================================================


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
    """Label the lines of a tree.

    Examples:
        >>> print(label_tree_lines(py_trees.behaviours.Dummy(), labels=["0"]))
        0: --> Dummy


        >>> tree = py_trees.composites.Sequence(
        ...             "S1",
        ...             False,
        ...             children=[
        ...                 py_trees.behaviours.Dummy(),
        ...                 py_trees.behaviours.Dummy()]
        ...         )


        >>> print(label_tree_lines(tree, labels=["A", "B", "C"]))
        A: [-] S1
        B:     --> Dummy
        C:     --> Dummy

        >>> print(label_tree_lines(tree, labels=["AAA", "BB", "C"]))
        AAA: [-] S1
         BB:     --> Dummy
          C:     --> Dummy

    """
    max_len = max([len(s) for s in labels])
    padded_labels = [s.rjust(max_len) for s in labels]

    tree_representation_lines = representation(tree).split("\n")
    enumerated_tree_representation_lines = [
        f"{i}: {t}" for i, t in zip(padded_labels, tree_representation_lines)
    ]

    output = "\n".join(enumerated_tree_representation_lines)
    return output


# TODO: Split each of these functions into one which
# returns a labeled representation of the tree,
# a mapping of allowed values to nodes and
# a separate function which does the prompting.
# This should help testing.


def prompt_identify_node(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which node?",
    display_nodes: bool = True,
) -> py_trees.behaviour.Behaviour:

    key_node_mapping = {str(i): n for i, n in enumerate_nodes(tree)}
    labels = key_node_mapping.keys()

    if display_nodes:
        text = f"{(label_tree_lines(tree=tree, labels=labels))}\n{message}"
    else:
        text = f"{message}"

    key = click.prompt(text=text, type=click.Choice(labels))

    node = key_node_mapping[key]

    return node


def prompt_identify_position(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which position?",
    display_nodes: bool = True,
) -> Tuple[py_trees.composites.Composite, int]:
    """
    Example:
        >>> s1 = py_trees.composites.Sequence("S1", False, children=[py_trees.behaviours.Dummy()])
        >>> prompt_identify_position(s1)
          [-] S1
        0: -->
              --> Dummy
        1: -->


        >>> s2 = py_trees.composites.Sequence("S2", False, children=[py_trees.behaviours.Failure()])
        >>> tree = py_trees.composites.Sequence("S0", False, children=[s1, s2])
        >>> prompt_identify_position(tree)
    """
    """
    Better Options:
        Option 0:
          [-] S0
        0: ----->
              [-] S1
        1: ------->
                --> Dummy
        2: ------->
        3: ----->
              [-] S2
        4: ------->
                --> Failure
        5: ------->
        6: ----->

        Option 1:
          [-] S0
        0: ----->
              [-] S1
        0.0: ------->
                --> Dummy
        0.1: ------->
        1: ----->
              [-] S2
        1.0: ------->
                --> Failure
        1.1: ------->
        2: ----->

        Option 2:
        [-] S0
            --> {0}
            [-] S1
              --> {0.0}
              --> Dummy
              --> {0.1}
            --> {1}
            [-] S2
              --> {1.0}
              --> Failure
              --> {1.1}
            --> {2}

        Option 3:
        [-] S0
            --> {1}
            [-] S1
              --> {2}
              --> Dummy
              --> {3}
            --> {4}
            [-] S2
              --> {5}
              --> Failure
              --> {6}
            --> {7}

        Option 4:
        [-] S0
            --> {⚡️ 1}
            [-] S1
                --> {⚡️ 2}
                --> Dummy
                --> {⚡️ 3}
            --> {⚡️ 4}
            [-] S2
                --> {⚡️ 5}
                --> Failure
                --> {⚡️ 6}
            --> {⚡️ 7}


        Option 5:
        Where: [before/after]
        Which: [user types display name]

        Option 6:
        [-] S0
            {⚡️ 1} <--
            [-] S1
                    {⚡️ 2} <--
                --> Dummy
                    {⚡️ 3} <--
                {⚡️ 4} <--
            [-] S2
                    {⚡️ 5} <--
                --> Failure
                    {⚡️ 6} <--
                {⚡️ 7} <--


        Option 7:
        [-] S0
            {⚡️ 1}
            [-] S1
                    {⚡️ 2}
                --> Dummy
                    {⚡️ 3}
                {⚡️ 4}
            [-] S2
                    {⚡️ 5}
                --> Failure
                    {⚡️ 6}
                {⚡️ 7}

        Option 8:
        [-] S0
            --> _1
            [-] S1
                --> _2
                --> Dummy
                --> _3
            --> _4
            [-] S2
                --> _5
                --> Failure
                --> _6
            --> _7

        Option 9:
        [-] S0
    1:       --> _
            [-] S1
    2:          --> _
                --> Dummy
    3:          --> _
    4:      --> _
            [-] S2
    5:          --> _
                --> Failure
    6:          --> _
    7:      --> _


        Option 10:
        [-] S0
    1:      --> ______
            [-] S1
    2:          --> ______
                --> Dummy
    3:          --> ______
    4:      --> ______
            [-] S2
    5:          --> ______
                --> Failure
    6:          --> ______
    7:      --> ______

    Option 11: Preview

    Chose a "Success" node:
        [-] S0
    1:      --> *Success*
            [-] S1
    2:          --> *Success*
                --> Dummy
    3:          --> *Success*
    4:      --> *Success*
            [-] S2
    5:          --> *Success*
                --> Failure
    6:          --> *Success*
    7:      --> *Success*

    """
    key_node_mapping = {str(i): n for i, n in enumerate_nodes(tree)}
    labels = []
    for key, node in key_node_mapping.items():
        if isinstance(node, py_trees.composites.Composite):
            labels.append(key)
        else:
            labels.append("_")

    if display_nodes:
        text = f"{(label_tree_lines(tree=tree, labels=labels))}\n{message}"
    else:
        text = f"{message}"

    key = click.prompt(text=text, type=click.Choice(labels))

    node = key_node_mapping[key]

    return node


def prompt_identify_composite(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which composite node?",
    display_nodes: bool = True,
    skip_label: str = "_"
) -> Tuple[py_trees.composites.Composite, int]:
    """
    Example:
        >>> s1 = py_trees.composites.Sequence("S1", False, children=[py_trees.behaviours.Dummy()])
        >>> prompt_identify_composite(s1)
          [-] S1
        0: -->
              --> Dummy
        1: -->


        >>> s2 = py_trees.composites.Sequence("S2", False, children=[py_trees.behaviours.Failure()])
        >>> tree = py_trees.composites.Sequence("S0", False, children=[s1, s2])
        >>> prompt_identify_position(tree)
    """
    key_node_mapping = {str(i): n for i, n in enumerate_nodes(tree)}
    labels = []
    for key, node in key_node_mapping.items():
        if isinstance(node, py_trees.composites.Composite):
            labels.append(key)
        else:
            labels.append(skip_label)
    if display_nodes:
        text = f"{(label_tree_lines(tree=tree, labels=labels))}\n{message}"
    else:
        text = f"{message}"
    allowed_labels = [l for l in labels if l != skip_label]
    key = click.prompt(text=text, type=click.Choice(allowed_labels))
    node = key_node_mapping[key]
    return node


def prompt_identify_child_index(
    tree: py_trees.behaviour.Behaviour,
    message: str = "Which position?",
    display_nodes: bool = True,
    skip_label: str = "_",
) -> int:
    labels = []
    i = 0
    for node in iterate_nodes(tree):
        if node in tree.children:
            labels.append(str(i))
            i += 1
        else:
            labels.append(skip_label)
    labels.append(str(i))

    if display_nodes:
        text = f"{(label_tree_lines(tree=tree, labels=labels))}\n{message}"
    else:
        text = f"{message}"
    allowed_labels = [l for l in labels if l != skip_label]
    key = click.prompt(text=text, type=click.Choice(allowed_labels))
    node_index = int(key)

    return node_index


def format_children_with_indices(composite: py_trees.composites.Composite) -> str:
    """
    Examples:
        >>> tree = py_trees.composites.Sequence("s1", False, children=[
        ...         py_trees.behaviours.Dummy(),
        ...         py_trees.behaviours.Success(),
        ...         s2 := py_trees.composites.Sequence("s2", False, children=[
        ...             py_trees.behaviours.Dummy(),
        ...         ]),
        ...         s3 := py_trees.composites.Sequence("", False, children=[
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

        >>> print(format_children_with_indices(s2))  # doctest: +NORMALIZE_WHITESPACE
        _:  [-] s2
        0:      --> Dummy

        >>> print(format_children_with_indices(s3))  # doctest: +NORMALIZE_WHITESPACE
        _:  [-]
        0:      --> Failure
        1:      --> p
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


def prompt_identify_library_node(
    library, message: str = "Which action from the library?", display_nodes: bool = True
) -> py_trees.behaviour.Behaviour:
    key_node_mapping = {str(i): n for i, n in enumerate(library)}

    if display_nodes:
        text = f"{format_library_with_indices(library)}\n{message}"
    else:
        text = f"{message}"
    index = click.prompt(text=text, type=click.Choice(key_node_mapping.keys()))

    node = key_node_mapping[index]

    return node


def format_library_with_indices(library: List[py_trees.behaviour.Behaviour]):
    return "\n".join([f"{i}: {n.name}" for i, n in enumerate(library)])


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
    i = click.prompt(text=text, type=click.IntRange(0, n_fs - 1))
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
        composite_node = prompt_identify_composite(
            tree, message="Which parent?")
        index = prompt_identify_child_index(composite_node)
        return composite_node, index
    elif annotation_ == str(NewNode):
        _logger.debug("in NewNode")
        new_node = prompt_identify_library_node(
            library, "Which node from the library?")
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
    library = [py_trees.behaviours.Success(), py_trees.behaviours.Failure()]
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
            # try:
            results = f(tree, library)
            _logger.debug(results)
            protocol.append(results)
            print(py_trees.display.ascii_tree(tree))

            # If we have any errors raised by the function, like wrong values,
            # we don't want to crash.
            # except (ValueError, IndexError, NotImplementedError) as e:
            #     _logger.error(f"\n{e}")
            #     continue

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
    tree, _ = load_experiment()
    i = prompt_identify_child_index(tree)
    main()
