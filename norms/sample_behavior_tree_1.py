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
"""

##############################################################################
# Imports
##############################################################################

import argparse
import sys
import time
import py_trees
import py_trees.console as console

##############################################################################
# Functions
##############################################################################

def description() -> str:
    """
    Print description and usage information about the program.

    Returns:
       the program description string
    """
    content = (
        "Testing out manual progressing tick in decision tree.\n"
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


class UserInputNode(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, shared_count: dict):
        super().__init__(name)
        self.status = py_trees.common.Status.RUNNING
        self.shared_count = shared_count
    

    def update(self) -> py_trees.common.Status:

        # user_input = input("Enter 's' for SUCCESS, 'f' for FAILURE: ").strip().lower()
        # if user_input == 's':
        #     return py_trees.common.Status.SUCCESS
        # elif user_input == 'f':
        #     return py_trees.common.Status.FAILURE
        # else:
        #     print("Invalid input, node will keep running.")
        #     return py_trees.common.Status.RUNNING

        time.sleep(2.0)  # Slow down the ticking process
        if self.shared_count['count'] == 0:
            self.shared_count['count'] += 1
            return py_trees.common.Status.FAILURE
        else:
            return py_trees.common.Status.SUCCESS




def create_root(blackboard: dict) -> py_trees.behaviour.Behaviour:
    """
    Create the root behaviour and its subtree.

    Returns:
        the root behaviour
    """
    root = py_trees.composites.Selector(name="Selector", memory=False)
    
    user_input_node = UserInputNode(name="User Input Node 1", shared_count=blackboard)
    always_running = py_trees.behaviours.Running(name="Running")
    user_input_node2 = UserInputNode(name="User Input Node", shared_count=blackboard)
    #always_running2 = py_trees.behaviours.Running(name="Running")

    root.add_children([user_input_node, user_input_node2, always_running])
    #root.add_children([user_input_node, always_running])

    return root

##############################################################################
# Main
##############################################################################

def main() -> None:
    """Entry point for the demo script."""
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    shared_count = {'count': 0}
    root = create_root(shared_count)
    behaviour_tree = py_trees.trees.BehaviourTree(root)

    ####################
    # Rendering
    ####################
    # if args.render:
    #     py_trees.display.render_dot_tree(root)
    #     sys.exit()

    ####################
    # Execute
    ####################
    root.setup_with_descendants()
    for i in range(1, 6):  # Tick 5 times
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            behaviour_tree.tick()
            
            if i%2 == 0:
                shared_count['count'] = 0

            print("\n")
            print(py_trees.display.unicode_tree(root=root, show_status=True))
            time.sleep(2.0)
        except KeyboardInterrupt:
            break
    print("\n")

if __name__ == "__main__":
    main()