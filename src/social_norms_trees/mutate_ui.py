from typing import Tuple, TypeVar
import py_trees

U = TypeVar("U", bound=py_trees.behaviour.Behaviour)
CompositeIndex = Tuple[py_trees.composites.Composite, int]


def remove(node: U) -> U:
    """Remove a behaviour from the tree

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


def insert(where: CompositeIndex, node: py_trees.behaviour.Behaviour) -> None:
    """
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
    where: CompositeIndex,
    node: py_trees.behaviour.Behaviour,
) -> None:
    """Move a node in the tree

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
    node0: py_trees.behaviour.Behaviour,
    node1: py_trees.behaviour.Behaviour,
) -> None:
    """Exchange two behaviours in the tree

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
