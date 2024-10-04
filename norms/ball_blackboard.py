#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
A py_trees demo.

.. argparse::
   :module: py_trees.demos.selector
   :func: command_line_argument_parser
   :prog: py-trees-demo-selector

.. graphviz:: dot/demo-selector.dot

.. image:: images/selector.gif

"""
##############################################################################
# Imports
##############################################################################

import argparse
import sys
import time
import typing
import operator

import py_trees
import py_trees.console as console

##############################################################################
# Classes
##############################################################################

py_trees.logging.level = py_trees.logging.Level.DEBUG
blackboard = py_trees.blackboard.Client(name="Client")
blackboard.register_key(key="isBallClose", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="isBallGrasped", access=py_trees.common.Access.WRITE)
blackboard.isBallClose = False
blackboard.isBallGrasped = False


def description() -> str:
    """
    Print description and usage information about the program.

    Returns:
       the program description string
    """
    content = (
        "Higher priority switching and interruption in the children of a selector.\n"
    )
    content += "\n"
    content += "In this example the higher priority child is setup to fail initially,\n"
    content += "falling back to the continually running second child. On the third\n"
    content += (
        "tick, the first child succeeds and cancels the hitherto running child.\n"
    )
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "Selectors".center(79) + "\n" + console.reset
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += banner_line
    else:
        s = content
    return s


def epilog() -> typing.Optional[str]:
    """
    Print a noodly epilog for --help.

    Returns:
       the noodly message
    """
    if py_trees.console.has_colours:
        return (
            console.cyan
            + "And his noodly appendage reached forth to tickle the blessed...\n"
            + console.reset
        )
    else:
        return None


def command_line_argument_parser() -> argparse.ArgumentParser:
    """
    Process command line arguments.

    Returns:
        the argument parser
    """
    parser = argparse.ArgumentParser(
        description=description(),
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r", "--render", action="store_true", help="render dot tree to file"
    )
    group.add_argument(
        "--render-with-blackboard-variables",
        action="store_true",
        help="render dot tree to file with blackboard variables",
    )
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="pause and wait for keypress at each tick",
    )
    return parser


def create_root() -> py_trees.behaviour.Behaviour:
    """
    Create the root behaviour and it's subtree.

    Returns:
        the root behaviour
    """
    root = py_trees.composites.Sequence(name="Sequence", memory=False)

    find = py_trees.behaviours.Success(name="Find Ball")

    pick_up_ball = py_trees.composites.Sequence(name="Sequence", memory=False)

    place = py_trees.behaviours.Success(name="Place Ball")

    root.add_children([find, pick_up_ball, place])

    move_to_ball = py_trees.composites.Selector(name="Selector", memory=False)

    obtain_ball = py_trees.composites.Selector(name="Selector", memory=False)

    pick_up_ball.add_children([move_to_ball, obtain_ball])

    print(blackboard)

    isClose = py_trees.behaviours.CheckBlackboardVariableValue(
        name="Ball Close?",
        check=py_trees.common.ComparisonExpression(
            variable="isBallClose", value=True, operator=operator.eq
        ),
    )

    approach = py_trees.behaviours.Running(name="Approach Ball")

    move_to_ball.add_children([isClose, approach])

    isGrasped = py_trees.behaviours.CheckBlackboardVariableValue(
        name="Ball Grasped?",
        check=py_trees.common.ComparisonExpression(
            variable="isBallGrasped", value=True, operator=operator.eq
        ),
    )

    grasp = py_trees.behaviours.Running(name="Grasp Ball")

    obtain_ball.add_children([isGrasped, grasp])

    return root


##############################################################################
# Main
##############################################################################


def main() -> None:
    """Entry point for the demo script."""
    args = command_line_argument_parser().parse_args()
    print(description())
    # print(blackboard)

    root = create_root()

    ####################
    # Rendering
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root)
        sys.exit()

    ####################
    # Execute
    ####################
    root.setup_with_descendants()
    print(py_trees.display.unicode_tree(root=root, show_status=True))
    for i in range(1, 6):
        try:
            time.sleep(1.0)
            print("\n--------- Tick {0} ---------\n".format(i))
            if i == 3:
                print("Ball is now close\n")
                blackboard.isBallClose = True
            if i == 5:
                print("Ball is now grasped\n")
                blackboard.isBallGrasped = True
                # blackboard.isBallClose = False
            root.tick_once()
            print("\n")
            print(py_trees.display.unicode_tree(root=root, show_status=True))
        except KeyboardInterrupt:
            break
    print("\n")


if __name__ == "__main__":
    main()
