from typing import Tuple, TypeVar
import py_trees

T = TypeVar("T", bound=py_trees.behaviour.Behaviour)
U = TypeVar("U", bound=py_trees.behaviour.Behaviour)
C = TypeVar("C", bound=py_trees.behaviour.Composite)

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


def insert_node(tree: T, node: py_trees.behaviour.Behaviour, parent: C, index: int) -> T:
    """
    Examples:
        
        >>> tree = py_trees.composites.Sequence("", False, children=[
        ...    py_trees.behaviours.Success()
        ... ])
        >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success

        >>> print(py_trees.display.ascii_tree(insert_node(tree, py_trees.behaviours.Failure(), 1)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Success
            --> Failure

        >>> print(py_trees.display.ascii_tree(insert_node(tree, py_trees.behaviours.Dummy(), 0)))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            --> Dummy
            --> Success
            --> Failure

    """
    parent.children.insert(index, node)
    return tree

# def move_node(
#     tree: T,
#     node: py_trees.behaviour.Behaviour,
#     new_parent: py_trees.behaviour.Behaviour,
#     index: int,
# ) -> T:
#     """Move a node in the tree

#     Examples:
#         >>> tree = py_trees.composites.Sequence("", False, children=[
#         ...     failure_node := py_trees.behaviours.Failure(),
#         ...     success_node := py_trees.behaviours.Success(),
#         ... ])
#         >>> print(py_trees.display.ascii_tree(tree))  # doctest: +NORMALIZE_WHITESPACE
#         [-]
#             --> Failure
#             --> Success

#         >>> print(py_trees.display.ascii_tree(move_node(tree, failure_node, tree, 1)))
#         ... # doctest: +NORMALIZE_WHITESPACE
#         [-]
#             --> Success
#             --> Failure
    

#     """

#     if node is None:
#         node = prompt_identify_node(tree, f"Which node do you want to move?")
#     if new_parent is None:
#         new_parent = prompt_identify_parent_node(
#             tree, f"What should its parent be?", display_nodes=True
#         )
#     if index is None:
#         index = prompt_identify_child_index(new_parent)

#     assert isinstance(new_parent, py_trees.composites.Composite)
#     assert isinstance(node.parent, py_trees.composites.Composite)

#     # old_parent = node.parent.name
#     node.parent.remove_child(node)
#     new_parent.insert_child(node, index)
        
#     return tree