import time
import click
from datetime import datetime
import json
import os
import uuid
import py_trees

from social_norms_trees.mutate_tree import move_node, exchange_nodes, remove_node
from social_norms_trees.serialize_tree import serialize_tree, deserialize_tree

DB_FILE = "db.json"


def load_db(db_file):
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            return json.load(f)
    else:
        return {}

def save_db(db, db_file):
    """Saves the Python dictionary back to db.json."""

    print(f"\nWriting results of simulation to {db_file}...")

    with open(db_file, "w") as f:
        json.dump(db, f, indent=4)

def experiment_setup(db):

    print("\n")
    participant_id = participant_login()

    print("\n")
    origin_tree = load_behavior_tree()

    experiment_id = initialize_experiment_record(db, participant_id, origin_tree)

    print("\nSetup Complete.\n")

    return participant_id, origin_tree, experiment_id


def participant_login():

    participant_id = click.prompt("Please enter your participant id", type=str)

    return participant_id


def get_behavior_trees():
    #TODO: Get behavior trees from respective data structure

    print("1. Original Tree")
    return [
        py_trees.composites.Sequence(
            "",
            False,
            children=[
                py_trees.behaviours.Dummy(),
                py_trees.behaviours.Dummy(),
                py_trees.composites.Sequence(
                    "",
                    False,
                    children=[
                        py_trees.behaviours.Success(),
                        py_trees.behaviours.Dummy(),
                    ],
                ),
                py_trees.composites.Sequence(
                    "",
                    False,
                    children=[
                        py_trees.behaviours.Dummy(),
                        py_trees.behaviours.Failure(),
                        py_trees.behaviours.Dummy(),
                        py_trees.behaviours.Running(),
                    ],
                ),
            ],
        )
    ]


def load_behavior_tree():
    
    tree_array = get_behavior_trees()
    tree_index = click.prompt("Please select a behavior tree to load for the experiment (enter the number)", type=int)
    return tree_array[tree_index - 1]


def initialize_experiment_record(db, participant_id, origin_tree):

    experiment_id = str(uuid.uuid4())

    #TODO: look into python data class

    #TODO: flatten structure of db to simply collction of experiment runs, that will include a field for the participant_id
    #instead of grouping by participants
    experiment_record = {
        "experiment_id": experiment_id,
        "participant_id": participant_id,
        "base_behavior_tree": serialize_tree(origin_tree),
        "start_date": datetime.now().isoformat(),
        "actions": [],
    }

    db[experiment_id] = experiment_record

    return experiment_id


def run_experiment(db, participant_id, origin_tree, experiment_id):

    # Loop for the actual experiment part, which takes user input to decide which action to take
    print("\nExperiment beginning...\n")

    while(True):
        
        print(py_trees.display.ascii_tree(origin_tree))
        user_choice = click.prompt(
            "Would you like to perform an action on the behavior tree?",
            show_choices=True,
            type=click.Choice(['y', 'n'], case_sensitive=False),
        )
    
        if user_choice == 'y':
            action = click.prompt(
                "1. move node\n" +
                "2. exchange node\n" + 
                "3. remove node\n" + 
                "Please select an action to perform on the behavior tree",
                type=click.Choice(['1', '2', '3'], case_sensitive=False),
                show_choices=True
            )

            if action == "1":
                db[experiment_id]["actions"].append("move node")
                move_node(origin_tree)
            elif action == "2":
                db[experiment_id]["actions"].append("exchange node")
                exchange_nodes(origin_tree)
            elif action == "3":
                db[experiment_id]["actions"].append("remove node")
                remove_node(origin_tree)
            else:
                print("Invalid choice, please select a valid number (1, 2, or 3).\n")

        else:
            db[experiment_id]["final_behavior_tree"] = serialize_tree(origin_tree)
            db[experiment_id]["end_date"] = datetime.now().isoformat()
            break
        
    return db
   


def main():
    print("AIT Prototype #1 Simulator")
    
    DB_FILE = "db.json"
    db = load_db(DB_FILE)


    participant_id, origin_tree, experiment_id = experiment_setup(db)
    db = run_experiment(db, participant_id, origin_tree, experiment_id)
    
    save_db(db, DB_FILE)
    

    print("\nSimulation has ended.")

    #TODO: visualize the differences between old and new behavior trees after experiment. 
    # Potentially use git diff 

if __name__ == "__main__":
    main()