import argparse
import sys
import py_trees
from action_library import action_library_2


def main():
    """
        tick_time: time between each node
    """
    # ------- Initialize the behavior tree -------

    root = py_trees.composites.Sequence(name="Sequence", memory=False)

    root.add_children([py_trees.behaviours.Dummy(name=action) for action in action_library_2["test_tree_1"].values()])

    behaviour_tree = py_trees.trees.BehaviourTree(root)




    # First, show the user the behavior tree
    print(py_trees.display.unicode_tree(root=root, show_status=True))
    
    #TODO: place these actions into a library of pre-defined actions
    # - a list of strings of actions
    # - this will also include the actions already defined in this tree, approach, go, open door 
    # - this list should update dynamically based on the context and what action is applicable
    
    # Get user input to decide which behavior to add
    for key, action in action_library_2["additional_actions"].items():
        print(f"{key}. {action}")         
    choice_index = input("Enter the number of which behavior to add to the tree: ")

    new_behavior = action_library_2["additional_actions"][int(choice_index)]

    print("\n")
    index = 1
    for x in root.children:
        print(f"{index}. {x.name}")
        index += 1
    # Get user to decide where to place new behavior in the tree
    index_choice = input("Enter the number of which behavior to place the new behavior in front of: ")

    if index_choice:
        # Insert the chosen behavior into the tree
        root.insert_child(py_trees.behaviours.Dummy(name=new_behavior), int(index_choice)-1)

    
 
    print("\nUpdated behavior tree:")
    print(py_trees.display.unicode_tree(root=root, show_status=True))

   

if __name__ == "__main__":

    main()