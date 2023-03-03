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

py_trees.logging.level = py_trees.logging.Level.INFO
blackboard = py_trees.blackboard.Client(name="Client")
blackboard.register_key(key="isCabinetUnlocked", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="isElevatorOpen", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="elevatorHasSpace", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="canEnterElevator", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="isElevatorOn7th", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="canLeaveElevator", access=py_trees.common.Access.WRITE)
blackboard.isCabinetUnlocked = False
blackboard.isElevatorOpen = False
blackboard.elevatorHasSpace = False
blackboard.canEnterElevator = False
blackboard.isElevatorOn7th = False
blackboard.canLeaveElevator = False

def description() -> str:
    """
    Print description and usage information about the program.

    Returns:
       the program description string
    """
    content = (
        "This is a demonstration of a medicine delivery robot decision tree process.\n"
    )
    content += "The robot needs to acquire the medicine, take the elevator to the 7th floor, and then deliver it to the patient.\n"
    content += "There are failing nodes within the tree that asks the human for input to demonstrate altering the tree between ticks.\n"
    content += "\n"
    content += "Key:\n"
    content += "'--> ' - A leaf node that can return success, failure, or running when ran.\n"
    content += "'\{-\} Sequence' - A sequential operator with children that will be run in sequential order.\n"
    content += "'\{o\} Selector' - A fallback operator with children that will be run one at a time if the previous child fails.\n"
    content += "'-' - A node that has not been ran in the current tick yet.\n"
    content += "'✕' - A node that has ran and failed in the current tick.\n"
    content += "'✓' - A node that has ran and succeeded in the current tick.\n"
    content += "'*' - A node that has ran and returned running in the current tick.\n"
    
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

def wait(name, ticks) -> py_trees.behaviours.StatusQueue:
    queue = []
    for i in range(0, ticks + 1):
        queue.append(py_trees.common.Status.RUNNING)
    return py_trees.behaviours.StatusQueue(
        name=name,
        queue=queue,
        eventually=py_trees.common.Status.FAILURE,
    )


def create_root() -> py_trees.behaviour.Behaviour:
    """
    Create the root behaviour and it's subtree.

    Returns:
        the root behaviour
    """
    # print(blackboard)

    root = py_trees.composites.Sequence(name="Sequence", memory=False)


    get_medicine = py_trees.composites.Sequence(name="Sequence", memory=False)

    take_elevator = py_trees.composites.Sequence(name="Sequence", memory=False)

    deliver_medicine = py_trees.composites.Sequence(name="Sequence", memory=False)

    root.add_children([get_medicine, take_elevator, deliver_medicine])



    go_to = py_trees.behaviours.Success(name="Go To Medicine Cabinet")
    unlock = py_trees.composites.Selector(name="Selector", memory=False)
    take = py_trees.behaviours.Success(name="Pickup Medicine")
    get_medicine.add_children([go_to, unlock, take])

    unlock_cabinet = py_trees.behaviours.CheckBlackboardVariableValue(
                name="Unlock Cabinet",
                check=py_trees.common.ComparisonExpression(
                    variable="isCabinetUnlocked", value=True, operator=operator.eq
                ),
            )

    wait_cabinet =  py_trees.behaviours.Running(name="Wait")
    supervisor = py_trees.behaviours.Success(name="Call Supervisor for Virtual Unlock")
    unlock.add_children([unlock_cabinet, wait_cabinet, supervisor])


    go_to_elevator = py_trees.behaviours.Success(name="Go to Elevator")
    click_up_button = py_trees.behaviours.Success(name="Click Up Button")
    wait_for_elevator = py_trees.composites.Sequence(name="Sequence", memory=False)
    enter_elevator = py_trees.composites.Sequence(name="Sequence", memory=False)

    take_elevator.add_children([go_to_elevator, click_up_button, wait_for_elevator, enter_elevator])

    is_elevator_open = py_trees.composites.Selector(name="Selector", memory=False)
    has_space_in_elevator = py_trees.composites.Selector(name="Selector", memory=False)
    can_enter_elevator = py_trees.composites.Selector(name="Selector", memory=False)
    wait_for_elevator.add_children([is_elevator_open, has_space_in_elevator, can_enter_elevator])


    elevator_open = py_trees.behaviours.CheckBlackboardVariableValue(
                name="Is Elevator Open?",
                check=py_trees.common.ComparisonExpression(
                    variable="isElevatorOpen", value=True, operator=operator.eq
                ),
            )
    wait_for_open_elevator = py_trees.behaviours.Running(name="Wait")
    supervisor = py_trees.behaviours.Success(name="Call Supervisor to Virtually Call Elevator")
    is_elevator_open.add_children([elevator_open, wait_for_open_elevator, supervisor])
    # is_elevator_open.add_children([elevator_open, wait_for_open_elevator])

    elevator_space = py_trees.behaviours.CheckBlackboardVariableValue(
                name=">= 9ft^2 of space in the Elevator?",
                check=py_trees.common.ComparisonExpression(
                    variable="elevatorHasSpace", value=True, operator=operator.eq
                ),
            )
    wait_for_space = py_trees.behaviours.Running(name="State \'I’ll wait\'")
    has_space_in_elevator.add_children([elevator_space, wait_for_space])
    
    elevator_enter = py_trees.behaviours.CheckBlackboardVariableValue(
                name="Ask to enter Elevator",
                check=py_trees.common.ComparisonExpression(
                    variable="canEnterElevator", value=True, operator=operator.eq
                ),
            )
    wait_to_enter_elevator = py_trees.behaviours.Running(name="State I’ll wait")
    can_enter_elevator.add_children([elevator_enter, wait_to_enter_elevator])





    enter_elevator_task = py_trees.behaviours.Success(name="Enter Elevator")
    hit_7th_floor_button = py_trees.behaviours.Success(name="Hit 7th Floor Button")
    enter_elevator.add_children([enter_elevator_task, hit_7th_floor_button])


    exit = py_trees.composites.Sequence(name="Sequence", memory=False)
    exit_statement = py_trees.behaviours.Success(name="State: I'll exit now")
    go_to_patient = py_trees.behaviours.Success(name="Go to Patient")
    deliver = py_trees.behaviours.Success(name="Deliver medicine to Patient")
    deliver_medicine.add_children([exit, exit_statement, go_to_patient, deliver])

    get_to_7th = py_trees.composites.Selector(name="Selector", memory=False)
    can_exit_now = py_trees.composites.Selector(name="Selector", memory=False)
    
    exit.add_children([get_to_7th, can_exit_now])

    is_elevator_on_7th = py_trees.behaviours.CheckBlackboardVariableValue(
                name="Is Elevator on 7th?",
                check=py_trees.common.ComparisonExpression(
                    variable="isElevatorOn7th", value=True, operator=operator.eq
                ),
            )
    elevator_wait = py_trees.behaviours.Running(name="Wait")
    get_to_7th.add_children([is_elevator_on_7th, elevator_wait])

    are_people_on_elevator = py_trees.behaviours.CheckBlackboardVariableValue(
                name="Is >= 1 Person in Elevator?",
                check=py_trees.common.ComparisonExpression(
                    variable="canLeaveElevator", value=True, operator=operator.eq
                ),
            )
    exit_elevator_wait = wait("Wait for at most 3 Ticks", 3)
    can_exit_now.add_children([are_people_on_elevator, exit_elevator_wait])








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
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.visitors.append(snapshot_visitor)
    print(py_trees.display.unicode_tree(root=root, show_status=True))
    tree_success = False
    i = 0
    time.sleep(1)
    while not tree_success:
        try:
            time.sleep(0.5)
            print("\n--------- Tick {0} ---------\n".format(i))
            # if i == 3:
            #     print("Cabinet is now unlocked\n")
            #     blackboard.isCabinetUnlocked = True
            # if i == 5:
            #     blackboard.isElevatorOpen = True
            if i == 7:
                blackboard.elevatorHasSpace = True
            if i == 9:
                blackboard.canEnterElevator = True
            if i == 11:
                blackboard.isElevatorOn7th = True
            if i == 13:
                blackboard.canLeaveElevator = True
            # if i == 15:
            #     blackboard.isElevatorOpen = True

            behaviour_tree.tick()
            print("\n")
            print(py_trees.display.unicode_tree(root=root, show_status=True))
            # ascii_tree = py_trees.display.ascii_tree(
            #     behaviour_tree.root)
            # print(ascii_tree)
            if behaviour_tree.root.status == py_trees.common.Status.SUCCESS:
                tree_success = True
            elif behaviour_tree.root.status == py_trees.common.Status.FAILURE:
                callSupervisor = input("Should the robot call it's supervisor for help on the next tick for the failed task? (1 for Yes 0 for No)\n")
                if callSupervisor == "1":
                    node = behaviour_tree.root
                    found = False
                    while not found:
                        for n in node.children:
                            if n.status == py_trees.common.Status.FAILURE:
                                node = n
                                break
                        if type(node) == py_trees.composites.Selector:
                            found = True
                    # supervisor = py_trees.behaviours.Success(name="Call Supervisor to " + node.name)
                    supervisor = py_trees.behaviours.Success(name="Call Supervisor for help")
                    node.add_children([supervisor])
            elif behaviour_tree.root.status == py_trees.common.Status.RUNNING:
                reduceDeontic = input("Should the robot reduce the deontic force of the current running task? (1 for Yes 0 for No)\n")
                if reduceDeontic == "1":
                    node = behaviour_tree.root
                    found = False
                    while not found:
                        for n in node.children:
                            if n.status == py_trees.common.Status.RUNNING:
                                node = n
                                break
                        if type(node) == py_trees.behaviours.Running:
                            found = True
                    # supervisor = py_trees.behaviours.Success(name="Call Supervisor to " + node.name)
                    parent = node.parent
                    parent.remove_child(node)
                    # supervisor = py_trees.behaviours.Success(name="Call Supervisor for help")
                    parent.add_children([node])

                    

            i += 1
        except KeyboardInterrupt:
            break
    print("\n")


main()