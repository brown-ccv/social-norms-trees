import argparse
import sys
import py_trees


def main(tick_time: float = 1):
    """
        tick_time: time between each node
    """
    # ------- Initialize the behavior tree -------

    root = py_trees.composites.Sequence(name="Sequence", memory=False)

    #approach_door
    approach_door = py_trees.behaviours.Dummy(name="approach_door")

    #go_through_door
    go_through_door = py_trees.behaviours.Dummy(name="go_through_door")

    #open_door 
    open_door = py_trees.behaviours.Dummy(name="open_door")

    root.add_children([approach_door, open_door, go_through_door])

    behaviour_tree = py_trees.trees.BehaviourTree(root)




    # First, show the user the behavior tree
    print(py_trees.display.unicode_tree(root=root, show_status=True))
    
    #TODO: place these actions into a library of pre-defined actions
    # - a list of strings of actions
    # - this will also include the actions already defined in this tree, approach, go, open door 
    # - this list should update dynamically based on the context and what action is applicable
    
    # Get user input to decide which behavior to add
    print("1. Knock on door")
    print("2. Sound siren")
    print("3. Turn around")
    print("4. Wait for an answer")
    behavior_choice = input("Enter the number of which behavior to add to the tree: ")

    if behavior_choice == "1":
        new_behavior = py_trees.behaviours.Dummy(name="knock_on_door")
    elif behavior_choice == "2":
        new_behavior = py_trees.behaviours.Dummy(name="sound_siren")
    elif behavior_choice == "3":
        new_behavior = py_trees.behaviours.Dummy(name="turn_around")


    print("\n")
    index = 1
    for x in root.children:
        print(f"{index}. {x.name}")
        index += 1
    # Get user to decide where to place new behavior in the tree
    index_choice = input("Enter the number of which behavior to place the new behavior in front of: ")

    if index_choice:
        # Insert the chosen behavior into the tree
        root.insert_child(new_behavior, int(index_choice)-1)

    

    print("\nUpdated behavior tree:")
    print(py_trees.display.unicode_tree(root=root, show_status=True))

   

if __name__ == "__main__":

    main()