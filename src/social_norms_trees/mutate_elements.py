import inspect
from functools import wraps
import logging
from types import GenericAlias
from typing import Tuple, TypeVar
import py_trees
from social_norms_trees.mutate_tree import (
    prompt_identify_node,
    prompt_identify_parent_node,
    prompt_identify_child_index,
    prompt_identify_library_node,
)

_logger = logging.getLogger(__name__)

ExistingNode = TypeVar("ExistingNode", bound=py_trees.behaviour.Behaviour)
NewNode = TypeVar("NewNode", bound=py_trees.behaviour.Behaviour)
CompositeIndex = TypeVar(
    "CompositeIndex", bound=Tuple[py_trees.composites.Composite, int]
)


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
            f"%s's parent is None, so we can't remove it. You can't remove the root node."
            % (node)
        )
        raise ValueError(msg)
    elif isinstance(node.parent, py_trees.composites.Composite):
        node.parent.remove_child(node)
    else:
        raise NotImplementedError()
    return node


def insert(node: NewNode, where: CompositeIndex) -> None:
    """
    Insert a new node.

    Examples:

        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success()
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

        >>> insert((tree, 1), py_trees.behaviours.Failure())
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> insert((tree, 0), py_trees.behaviours.Dummy())
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
        >>> move((tree, 1), failure_node)
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

            >>> move((tree, 1), failure_node)
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

    """
    parent, index = where
    insert((parent, index), remove(node))
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
    """

    node0_parent, node0_index = node0.parent, node0.parent.children.index(node0)
    node1_parent, node1_index = node1.parent, node1.parent.children.index(node1)

    move((node1_parent, node1_index), node0)
    move((node0_parent, node0_index), node1)

    return


def mutate_ui(f):
    """Factory function for a tree mutator UI"""

    signature = inspect.signature(f)

    @wraps(f)
    def f_inner(tree, library):
        kwargs = {}
        for parameter_name in signature.parameters.keys():
            annotation = signature.parameters[parameter_name].annotation
            _logger.debug(f"getting arguments for {annotation=}")
            value = _get_mutate_arguments(str(annotation), tree, library)
            kwargs[parameter_name] = value
        f(**kwargs)
        return {"tree": tree, "function": f, "kwargs": kwargs}

    return f_inner


def _get_mutate_arguments(annotation: str, tree, library):
    assert isinstance(annotation, str)

    if annotation == str(inspect.Parameter.empty):
        _logger.debug("in empty")
        msg = "Can't work out what argument %s should be" % annotation
        raise ValueError(msg)
    elif annotation == str(ExistingNode):
        _logger.debug("in ExistingNode")
        node = prompt_identify_node(tree)
        return node
    elif annotation == str(CompositeIndex):
        _logger.debug("in CompositeIndex")
        composite_node = prompt_identify_parent_node(tree)
        index = prompt_identify_child_index(composite_node)
        return composite_node, index
    elif annotation == str(NewNode):
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


if __name__ == "__main__":
    import py_trees

    logging.basicConfig(level=logging.DEBUG)

    def init_tree():
        tree = py_trees.composites.Sequence(
            "",
            False,
            children=[
                py_trees.behaviours.Dummy("A"),
                py_trees.composites.Sequence(
                    "Sq",
                    memory=False,
                    children=[
                        py_trees.behaviours.Dummy("B"),
                        py_trees.behaviours.Dummy("C"),
                        py_trees.behaviours.Dummy("D"),
                    ],
                ),
                py_trees.composites.Selector(
                    "Sl",
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

    # tree, library = init_tree()
    # mutate_ui(remove)(tree, library)
    # print(py_trees.display.ascii_tree(tree))

    # tree, library = init_tree()
    # print(py_trees.display.ascii_tree(tree))
    # mutate_ui(move)(tree, library)
    # print(py_trees.display.ascii_tree(tree))

    tree, library = init_tree()
    mutate_ui(insert)(tree, library)
    print(py_trees.display.ascii_tree(tree))
