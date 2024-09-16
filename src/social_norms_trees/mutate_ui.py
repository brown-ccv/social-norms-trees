from typing import Tuple, TypeVar
import py_trees

T = TypeVar("T", bound=py_trees.behaviour.Behaviour)
U = TypeVar("U", bound=py_trees.behaviour.Behaviour)
V = TypeVar("V", bound=py_trees.behaviour.Behaviour)
C = TypeVar("C", bound=py_trees.composites.Composite)

def remove_node(tree: T, node: U) -> Tuple[T, U]:
    """Remove a behaviour from the tree

    Examples:
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success(),
        ...    failure_node := py_trees.behaviours.Failure()])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> tree, removed_node = remove_node(tree, failure_node)
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

    """
    if node.parent is None:
        msg = f"%s's parent is None, so we can't remove it. You can't remove the root node." % (node)
        raise ValueError(msg)
    elif isinstance(node.parent, py_trees.composites.Composite):
        node.parent.remove_child(node)
    else:
        raise NotImplementedError()
    return tree, node


def insert_node(tree: T, parent: C, index: int, node: py_trees.behaviour.Behaviour) -> T:
    """
    Examples:
        
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success()
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

        >>> print(py_trees.display.ascii_tree(insert_node(tree, tree, 1, py_trees.behaviours.Failure())))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> print(py_trees.display.ascii_tree(insert_node(tree, tree, 0, py_trees.behaviours.Dummy())))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Dummy
            --> Success
            --> Failure

    """
    parent.insert_child(node, index)
    return tree

def move_node(
    tree: T,
    parent: py_trees.behaviour.Behaviour,
    index: int,
    node: py_trees.behaviour.Behaviour,
) -> T:
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

        >>> print(py_trees.display.ascii_tree(tree := move_node(tree, tree, 1, failure_node)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> print(py_trees.display.ascii_tree(move_node(tree, tree, 1, failure_node)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure
    
    """
    tree_without_node, removed_node = remove_node(tree, node)
    tree_with_moved_node = insert_node(tree_without_node, parent, index, removed_node)
    return tree_with_moved_node

def exchange_nodes(
        tree: T,
        node0: U,
        node1: V,
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

    node0_parent, node0_index = node0.parent, node0.parent.children.index(node0)
    node1_parent, node1_index = node1.parent, node1.parent.children.index(node1)

    tree = move_node(tree, node1_parent, node1_index, node0)
    tree = move_node(tree, node0_parent, node0_index, node1)

    return tree