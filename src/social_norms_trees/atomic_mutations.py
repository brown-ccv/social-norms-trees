from collections import namedtuple
import inspect
from functools import partial, wraps
import logging
from types import GenericAlias
from typing import Callable, List, Mapping, NamedTuple, Tuple, TypeVar, Union, Dict
from colorama import Fore, Back, Style

import click
import py_trees
import typer

_logger = logging.getLogger(__name__)

# =============================================================================
# Argument types
# =============================================================================

ExistingNode = TypeVar("ExistingNode", bound=py_trees.behaviour.Behaviour)
NewNode = TypeVar("NewNode", bound=py_trees.behaviour.Behaviour)
CompositeIndex = TypeVar(
    "CompositeIndex", bound=Tuple[py_trees.composites.Composite, int]
)
BehaviorIdentifier = TypeVar(
    "BehaviorIdentifier", bound=Union[ExistingNode, NewNode, CompositeIndex]
)
BehaviorTreeNode = TypeVar("BehaviorTreeNode", bound=py_trees.behaviour.Behaviour)
BehaviorTree = TypeVar("BehaviorTree", bound=BehaviorTreeNode)
BehaviorLibrary = TypeVar("BehaviorLibrary", bound=List[BehaviorTreeNode])
TreeOrLibrary = TypeVar("TreeOrLibrary", bound=Union[BehaviorTree, BehaviorLibrary])


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
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
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
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
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

        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
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

        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
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

        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
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

        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] 1
                --> A
            [-] 2
                --> B

        >>> exchange(a, b)
        >>> print(py_trees.display.ascii_tree(tree))
        ... # doctest: +NORMALIZE_WHITESPACE
        [-]
            [-] 1
                --> B
            [-] 2
                --> A
    """

    node0_parent = node0.parent
    node0_index = node0.parent.children.index(node0)
    node1_parent = node1.parent
    node1_index = node1.parent.children.index(node1)

    move(node0, (node1_parent, node1_index))
    move(node1, (node0_parent, node0_index))

    return


# =============================================================================
# Node and Position Selectors
# =============================================================================


def iterate_nodes(tree: py_trees.behaviour.Behaviour):
    """
    Examples:
        >>> list(iterate_nodes(py_trees.behaviours.Dummy()))
        ... # doctest: +ELLIPSIS
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

        >>> list(enumerate_nodes(py_trees.behaviours.Dummy()))
        ... # doctest: +ELLIPSIS
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

        If there are more labels than lines, then those are shown too:
        >>> print(label_tree_lines(tree, labels=["AAA", "BB", "C", "O"]))
        AAA: [-] S1
         BB:     --> Dummy
          C:     --> Dummy
          O:
    """
    max_len = max([len(s) for s in labels])
    padded_labels = [s.rjust(max_len) for s in labels]

    tree_representation_lines = representation(tree).split("\n")

    enumerated_tree_representation_lines = [
        # Make the line. If `t` is missing,
        # then we don't want a trailing space
        # so we strip that away
        #TODO: update color
        f"{Fore.WHITE}{{{i}}}: {t}{Style.RESET_ALL}".rstrip()
        for i, t in zip(padded_labels, tree_representation_lines)
    ]

    output = "\n".join(enumerated_tree_representation_lines)
    return output


# TODO: Split each of these functions into one which
# returns a labeled representation of the tree,
# a mapping of allowed values to nodes and
# a separate function which does the prompting.
# This should help testing.

# Edge cases: what happens if the name of a node is really long - does the ascii representation wrap around?


class NodeMappingRepresentation(NamedTuple):
    mapping: Dict[str, py_trees.behaviour.Behaviour]
    labels: List[str]
    representation: str

def prompt_identify(
    tree: TreeOrLibrary,
    function: Callable[
        [TreeOrLibrary], Tuple[Mapping[str, BehaviorIdentifier], List[str], str]
    ],
    message: str = "Which?",
    display_nodes: bool = True,
) -> BehaviorIdentifier:

    mapping, labels, representation = function(tree)

    if display_nodes:
        text = f"{representation}\n{message}"
    else:
        text = f"{message}"

    key = click.prompt(text=text, type=click.Choice(labels))
    value = mapping[key]
    return value

def get_node_mapping(tree: BehaviorTree) -> NodeMappingRepresentation:
    """
    Examples:
        >>> a = get_node_mapping(py_trees.behaviours.Dummy())
        >>> a.mapping
        {'0': <py_trees.behaviours.Dummy object at 0x...>}

        >>> a.labels
        ['0']

        >>> print(a.representation)
        0: --> Dummy

        >>> b = get_node_mapping(py_trees.composites.Sequence("", False, children=[py_trees.behaviours.Dummy()]))
        >>> b.mapping  # doctest: +NORMALIZE_WHITESPACE
        {'0': <py_trees.composites.Sequence object at 0x...>,
         '1': <py_trees.behaviours.Dummy object at 0x...>}

        >>> b.labels
        ['0', '1']

        >>> print(b.representation)
        0: [-]
        1:     --> Dummy

    """
    #TODO: should we remove index 0 for root node? 
    mapping = {str(i): n for i, n in enumerate_nodes(tree)}
    labels = list(mapping.keys())
    representation = label_tree_lines(tree=tree, labels=labels)
    return NodeMappingRepresentation(mapping, labels, representation)


prompt_identify_node = partial(prompt_identify, function=get_node_mapping)


def get_library_mapping(library: BehaviorLibrary) -> NodeMappingRepresentation:
    """
    Examples:
        >>> from py_trees.behaviours import Success, Failure
        >>> n = get_library_mapping([])
        >>> n.mapping
        {}

        >>> n.labels
        []

        >>> print(n.representation)
        <BLANKLINE>

        >>> a = get_library_mapping([Success(), Failure()])
        >>> a.mapping  # doctest: +NORMALIZE_WHITESPACE
        {'0': <py_trees.behaviours.Success object at 0x...>,
         '1': <py_trees.behaviours.Failure object at 0x...>}

        >>> a.labels
        ['0', '1']

        >>> print(a.representation)
        0: Success
        1: Failure
    """

    mapping = {str(i): n for i, n in enumerate(library)}
    labels = list(mapping.keys())
    representation = "\n".join([f"{i}: {n.name}" for i, n in enumerate(library)])
    return NodeMappingRepresentation(mapping, labels, representation)


prompt_identify_library_node = partial(prompt_identify, function=get_library_mapping)


def get_composite_mapping(tree: BehaviorTree, skip_label="_"):
    """
    Examples:
        >>> a = get_composite_mapping(py_trees.behaviours.Dummy())
        >>> a.mapping
        {}

        >>> a.labels
        []

        >>> print(a.representation)
        _: --> Dummy

        >>> b = get_composite_mapping(py_trees.composites.Sequence("", False, children=[py_trees.behaviours.Dummy()]))
        >>> b.mapping  # doctest: +NORMALIZE_WHITESPACE
        {'0': <py_trees.composites.Sequence object at 0x...>}

        >>> b.labels
        ['0']

        >>> print(b.representation)
        0: [-]
        _:     --> Dummy
    """
    mapping = {}
    display_labels, allowed_labels = [], []

    for i, node in enumerate_nodes(tree):
        label = str(i)
        if isinstance(node, py_trees.composites.Composite):
            mapping[label] = node
            display_labels.append(label)
            allowed_labels.append(label)
        else:
            display_labels.append(skip_label)
    representation = label_tree_lines(tree=tree, labels=display_labels)

    return NodeMappingRepresentation(mapping, allowed_labels, representation)


prompt_identify_composite = partial(prompt_identify, function=get_composite_mapping)

class TreeInsertionState:
    def __init__(self):
        self.index_mapping = {}
        self.parent_child_mapping = {}
        self.tree_representation = ""

def _append_line(state, content, level):
    """
    Appends a line representing an existing node to the tree representation string.
    """
    # state.tree_representation += Fore.LIGHTBLACK_EX + ('   ' * level + content) + "\n"
    state.tree_representation += ('   ' * level + content) + "\n"

def _append_insertion_point(state, content, level):
    """
    Appends a line representing an insertion point to the tree representation string.
    """
    # state.tree_representation += Fore.WHITE + ('   ' * level + content) + "\n"
    state.tree_representation += ('   ' * level + content) + "\n"

def _create_insertion_point(state, parent_node, level):
    """
    Create relevant insertion point(s) for a given parent node and updates the state with the new insertion index.
    """
    insertion_index = str(len(state.index_mapping))
    _append_insertion_point(state, f"--> {{{insertion_index}}}", level)
    state.index_mapping[insertion_index] = parent_node

    if parent_node in state.parent_child_mapping:
        state.parent_child_mapping[parent_node].append(insertion_index)
    else:
        state.parent_child_mapping[parent_node] = [insertion_index]

    
def _build_tree_with_insertion_points(node, state, level=0):
    """
    Recursively traverses the tree to construct a string representation with all possible insertion points,
    while updating the state to reflect the current parent-node hierarchy and insertion mappings.

    Examples: 

        >>> tree = py_trees.composites.Sequence("S0", memory = False, children = [])
        >>> state = TreeInsertionState()
        >>> res = _build_tree_with_insertion_points(tree, state)
        >>> print(res.tree_representation)
        [-] S0
           --> {0}
        <BLANKLINE>

        >>> tree2 = py_trees.composites.Sequence("S0", memory = False, children = [
        ... py_trees.behaviours.Dummy()])
        >>> state2 = TreeInsertionState()
        >>> res2 = _build_tree_with_insertion_points(tree2, state2)
        >>> print(res2.tree_representation)
        [-] S0
           --> {0}
           --> Dummy
           --> {1}
        <BLANKLINE>
        
        >>> tree3 = py_trees.composites.Sequence("S0", memory = False, children = [
        ... py_trees.composites.Sequence("S1", memory = False, children = [])])
        >>> state3 = TreeInsertionState()
        >>> res3 = _build_tree_with_insertion_points(tree3, state3)
        >>> print(res3.tree_representation)
        [-] S0
           --> {0}
           [-] S1
              --> {1}
           --> {2}
        <BLANKLINE>
    """

    # Create an insertion point before this node, but only if its not the root level 
    if level != 0:
        _create_insertion_point(state, node.parent, level)


    # Display the current node
    _append_line(state, f"[-] {node.name}", level)

    #edge case, if sequence node exists but there are no children defined, set child node as potential insertion point
    if not node.children:
        _create_insertion_point(state, node, level+1)

    # Iterate through each child node
    for child in node.children:
        #For selector and sequence nodes
        if isinstance(child, py_trees.composites.Composite):
            # Recursive call on each child node
            _build_tree_with_insertion_points(child, state, level+1)
            # Create additional insertion point after the last child of this composite node
            if child == (node.children[-1]):
                _create_insertion_point(state, node, level + 1)

        else:
            #For leaf nodes, create insertion point before the leaf node first
            _create_insertion_point(state, node, level + 1)
            #display the leaf node
            _append_line(state, f"--> {child.name}", level + 1)
            #Create additional insertion point after the last leaf node
            if child == (node.children[-1]):
                _create_insertion_point(state, node, level + 1)
    
    
    return state


def get_insert_mapping(tree: BehaviorTree):
    """
    Examples: 

        >>> child_node_1 = py_trees.behaviours.Dummy()
        >>> sequence_node_1 = py_trees.composites.Sequence("S1", False, children=[])
        >>> root_node_1 = py_trees.composites.Sequence("S0", False, children=[child_node_1, sequence_node_1])

        >>> a = get_insert_mapping(root_node_1)
        
        >>> list(a.labels)
        ['0', '1', '2', '3']
        
        >>> a.mapping["0"][0] == root_node_1
        True
        >>> a.mapping["2"][0] == sequence_node_1
        True
        >>> a.mapping["3"][0] == root_node_1
        True

        >>> a.mapping["0"][1] == 0
        True
        >>> a.mapping["1"][1] == 1
        True
        >>> a.mapping["2"][1] == 0
        True
        >>> a.mapping["3"][1] == 2
        True

        >>> print(a.representation)
        [-] S0
           --> {0}
           --> Dummy
           --> {1}
           [-] S1
              --> {2}
           --> {3}
        <BLANKLINE>
    """

    state = TreeInsertionState()
    _build_tree_with_insertion_points(tree, state)
    #create mapping where each label maps to a tuple:
    #first element is the parent node reference for the current label index
    #second element is the index of the label in its parent's child list in parent_child_mapping
    mapping = {
    label: (
        state.index_mapping[label],  #parent node reference
        state.parent_child_mapping[state.index_mapping[label]].index(label)  #position in parent's child list
        )
        for label in state.index_mapping.keys()
    }    
    
    labels = state.index_mapping.keys()

    return NodeMappingRepresentation(mapping, labels, state.tree_representation)


prompt_identify_insertion_index = partial(
    prompt_identify,
    function=get_insert_mapping
)

def get_child_index_mapping(tree: BehaviorTree, skip_label="_"):
    """
    Examples:
        >>> a = get_child_index_mapping(py_trees.behaviours.Dummy())
        >>> a.mapping
        {'0': 0}

        >>> a.labels
        ['0']

        >>> print(a.representation)
        _: --> Dummy
        0:

        >>> b = get_child_index_mapping(py_trees.composites.Sequence("", False, children=[py_trees.behaviours.Dummy()]))
        >>> b.mapping  # doctest: +NORMALIZE_WHITESPACE
        {'0': 0, '1': 1}

        >>> b.labels
        ['0', '1']

        >>> print(b.representation)
        _: [-]
        0:     --> Dummy
        1:
    """
    mapping = {}
    display_labels, allowed_labels = [], []

    for node in iterate_nodes(tree):
        if node in tree.children:
            index = tree.children.index(node)
            label = str(index)
            mapping[label] = index
            allowed_labels.append(label)
            display_labels.append(label)
        else:
            display_labels.append(skip_label)

    # Add the "after all the elements" label
    post_list_index = len(tree.children)
    post_list_label = str(post_list_index)
    allowed_labels.append(post_list_label)
    display_labels.append(post_list_label)
    mapping[post_list_label] = post_list_index

    representation = label_tree_lines(tree=tree, labels=display_labels)

    return NodeMappingRepresentation(mapping, allowed_labels, representation)


prompt_identify_child_index = partial(prompt_identify, function=get_child_index_mapping)


def get_position_mapping(tree):
    """

    For insert and move node actions

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
        
    For exchange and remove node actions

        {0} [-] Sequence0
        {1}     [-] Sequence1
        {2}         --> Dummy1
        {3}         --> Dummy2
        {4}     --> Dummy2
        {5}     [o] Sequence2
        {6}         --> Failure
        {7}         --> Dummy3

        
    Both will follow color scheme 

    """
    pass


# =============================================================================
# User Interface
# =============================================================================


# Wrapper functions for the atomic operations which give them a UI.
MutationResult = namedtuple("MutationResult", ["result", "tree", "function", "kwargs"])


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
    f: Callable,
) -> Callable[
    [py_trees.behaviour.Behaviour, List[py_trees.behaviour.Behaviour]], MutationResult
]:
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
        _logger.debug(return_value)
        return return_value

    return f_inner


def prompt_get_mutate_arguments(annotation: GenericAlias, tree, library):
    """Prompt the user to specify nodes and positions in the tree."""
    annotation_ = str(annotation)
    assert isinstance(annotation_, str)

    if annotation_ == str(inspect.Parameter.empty):
        _logger.debug("No argument annotation, returning None")
        return None
    elif annotation_ == str(ExistingNode):
        _logger.debug("in ExistingNode")
        node = prompt_identify_node(tree)
        return node
    elif annotation_ == str(CompositeIndex):
        _logger.debug("in CompositeIndex")
        #instead of getting parent node, then children index, we simply ask for one index. 
        #from one index, we determine the values "composite_node" and "index"
        #and return
        composite_node, index = prompt_identify_insertion_index(tree)
        return composite_node, index
    elif annotation_ == str(NewNode):
        _logger.debug("in NewNode")
        new_node = prompt_identify_library_node(
            library, message="Which node from the library?"
        )
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


def end_experiment():
    """I'm done, end the experiment."""
    raise QuitException("User ended the experiment.")


# =============================================================================
# Main Loop
# =============================================================================


def load_experiment():
    """Placeholder function for loading a tree and library (should come from a file)."""
    tree = py_trees.composites.Sequence(
        "Sequence0",
        False,
        children=[
            py_trees.composites.Sequence(
                "Sequence1",
                memory=False,
                children=[
                    py_trees.behaviours.Dummy("Dummy1"),
                    py_trees.behaviours.Dummy("Dummy2"),
                ],
            ),
            py_trees.behaviours.Dummy("Dummy2"),
            py_trees.composites.Selector(
                "Sequence2",
                memory=False,
                children=[
                    py_trees.behaviours.Failure(),
                    py_trees.behaviours.Dummy("Dummy3"),
                ],
            ),
        ],
    )
    library = [py_trees.behaviours.Success(), py_trees.behaviours.Failure()]
    return tree, library


def save_results(tree, protocol):
    _logger.info("saving results")
    print(f"protocol: {protocol}")
    print(f"tree:\n{py_trees.display.unicode_tree(tree)}")


app = typer.Typer()


@app.command()
def main():
    logging.basicConfig(level=logging.DEBUG)
    tree, library = load_experiment()
    protocol = []

    # The main loop of the experiment
    while f := mutate_chooser(insert, move, exchange, remove, end_experiment):
        results = f(tree, library)
        _logger.debug(results)
        protocol.append(results)
        print(py_trees.display.ascii_tree(tree))


if __name__ == "__main__":
    app()
