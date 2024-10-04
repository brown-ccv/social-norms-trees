import time
import click
from datetime import datetime
import json
import os
import uuid
import py_trees

from social_norms_trees.mutate_tree import move_node, exchange_nodes, remove_node, add_node
from social_norms_trees.serialize_tree import serialize_tree, deserialize_tree

from social_norms_trees.behavior_library import BehaviorLibrary

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

def experiment_setup(db, origin_tree):

    print("\n")
    participant_id = participant_login()

    experiment_id = initialize_experiment_record(db, participant_id, origin_tree)

    print("\nSetup Complete.\n")

    return participant_id, experiment_id


def participant_login():

    participant_id = click.prompt("Please enter your participant id", type=str)

    return participant_id


def load_resources(file_path):
    try:
        print(f"\nLoading behavior tree and behavior library from {file_path}...\n")
        with open(file_path, 'r') as file:
            resources = json.load(file)
    
    except json.JSONDecodeError:
        raise ValueError("Error")
    except Exception:
        raise RuntimeError("Error")
    

    behavior_tree = resources.get('behavior_tree')
    behavior_list = resources.get('behavior_library')
    context_paragraph = resources.get('context')

    behavior_library = BehaviorLibrary(behavior_list)

    behavior_tree = deserialize_tree(behavior_tree, behavior_library)

    print("Loading success.")
    return behavior_tree, behavior_library, context_paragraph

def initialize_experiment_record(db, participant_id, origin_tree):

    experiment_id = str(uuid.uuid4())

    #TODO: look into python data class

    experiment_record = {
        "experiment_id": experiment_id,
        "participant_id": participant_id,
        "base_behavior_tree": serialize_tree(origin_tree),
        "start_date": datetime.now().isoformat(),
        "action_history": [],
    }

    db[experiment_id] = experiment_record

    return experiment_id


def run_experiment(db, origin_tree, experiment_id, behavior_library):

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
                "4. add node\n" +
                "Please select an action to perform on the behavior tree",
                type=click.Choice(['1', '2', '3', '4'], case_sensitive=False),
                show_choices=True
            )

            if action == "1":
                origin_tree, action_log = move_node(origin_tree)
                db[experiment_id]["action_history"].append(action_log)
            elif action == "2":
                origin_tree, action_log = exchange_nodes(origin_tree)
                db[experiment_id]["action_history"].append(action_log)

            elif action == "3":
                origin_tree, action_log = remove_node(origin_tree)
                db[experiment_id]["action_history"].append(action_log)

            elif action == "4":
                origin_tree, action_log = add_node(origin_tree, behavior_library)
                db[experiment_id]["action_history"].append(action_log)

            else:
                print("Invalid choice, please select a valid number (1, 2, or 3).\n")

        else:
            db[experiment_id]["final_behavior_tree"] = serialize_tree(origin_tree)
            db[experiment_id]["end_date"] = datetime.now().isoformat()
            break
        
    return db
   


def main():
    print("AIT Prototype #1 Simulator")
    

    #TODO: write up some context, assumptions made in the README 

    #TODO: user query for files
    DB_FILE = "db.json"
    db = load_db(DB_FILE)

    #load tree to run experiment on, and behavior library
    
    RESOURCES_FILE = "resources.json"
    original_tree, behavior_library, context_paragraph = load_resources(RESOURCES_FILE)

    print(f"\nContext of this experiment: {context_paragraph}")

    participant_id, experiment_id = experiment_setup(db, original_tree)
    db = run_experiment(db, original_tree, experiment_id, behavior_library)
    
    save_db(db, DB_FILE)

    #TODO: define export file, that will be where we export the results to
    

    print("\nSimulation has ended.")

    #TODO: visualize the differences between old and new behavior trees after experiment. 
    # Potentially use git diff 

if __name__ == "__main__":
    main()