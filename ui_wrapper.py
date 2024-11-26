import logging
import pathlib
from typing import Annotated, List
import click
from datetime import datetime
import json
import os
import uuid
import traceback
import time

import typer

from behavior_tree_library import Behavior, Sequence
from atomic_mutations import remove, insert, move
from colorama import Fore, Back, Style

from interactive_ui import run_interactive_list

# import keyboard  # Make sure to install this module with `pip install keyboard`



def load_db(db_file):
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            return json.load(f)
    else:
        return {}


def save_db(db, db_file):
    """Saves the Python dictionary back to db.json."""

    print(f"\nWriting results of simulation to {db_file}...")

    json_representation = json.dumps(db, indent=4)

    with open(db_file, "w") as f:
        f.write(json_representation)


def  experiment_setup(db):
    print("\n")
    participant_id = participant_login()

    experiment_id = initialize_experiment_record(db, participant_id)

    print("\nSetup Complete.\n")

    return participant_id, experiment_id


def participant_login():
    #TODO: prompt for name instead of id
    participant_id = click.prompt("Please enter your participant id", type=str)

    return participant_id




def deserialize_behaviors(behaviors):
    deserialized_behaviors = {}

    for behavior in behaviors:
        deserialized_behaviors[behavior["id"]] = Behavior(id=behavior["id"], name=behavior["name"])

    return deserialized_behaviors


def build_tree(context, children, behaviors):
    
    children_behaviors = []
    
    parent_node = Sequence(
        name=context,
    )

    for behavior_id in children:
        behaviors[behavior_id].parent = parent_node
        children_behaviors.append(behaviors[behavior_id])
    
    return Sequence(
        name=context,
        children= children_behaviors
    )

def serialize_tree(behavior_tree):
    children_list = []
    
    for node in behavior_tree.children:
        children_list.append(node.id)
    return children_list
        
#behaviors = deserialized behavious
#behavior_list = array of all behaviors
def build_behavior_bank(behaviors, behavior_list):
    behavior_bank = []

    for behavior in behavior_list:
        if "in_behavior_bank" in behavior and behavior["in_behavior_bank"]:
            behavior_bank.append(behaviors[behavior["id"]])
    return behavior_bank



def display_tree(node, indent=0):
    """Recursively display the behavior tree in a readable format."""
    if isinstance(node, Sequence):
        print(" " * indent + node.name)
        if node.children:
            for child in node.children:
                display_tree(child, indent + 4)
    elif isinstance(node, Behavior):
        print(" " * indent + " -> " +  node.name)

def load_resources(file_path):
    try:
        print(f"\nLoading behavior tree and behavior library from {file_path}...\n")
        with open(file_path, "r") as file:
            resources = json.load(file)

    except json.JSONDecodeError:
        raise ValueError("Error")
    except Exception:
        raise RuntimeError("Error")

    all_resources = {}

    for subtree in resources:
        
        children = resources[subtree].get("children")
        behavior_list = resources[subtree].get("behavior_library")
        context_paragraph = resources[subtree].get("context")

        #deserialize behavior_list
        deserialized_behaviors = deserialize_behaviors(behavior_list)
        
        #then use it to build the subgoal behavior tree
        sub_tree = build_tree(context_paragraph, children, deserialized_behaviors)

        behavior_bank = build_behavior_bank(deserialized_behaviors, behavior_list)

        all_resources[subtree] = {
            "context": context_paragraph,
            "behaviors": behavior_bank,
            "sub_tree": sub_tree
        }
       
    return all_resources

def initialize_experiment_record(db, participant_id):
    experiment_id = str(uuid.uuid4())

    # TODO: look into python data class

    experiment_record = {
        "experiment_id": experiment_id,
        "participant_id": participant_id,
        "experiment_start_date": datetime.now().isoformat(),
        "experiment_progression": {}
    }

    db[experiment_id] = experiment_record

    return experiment_id

def summarize_behaviors_check(subgoal_resources, db):
    print("Bot: Here are the actions, in order, that I will take to achieve this goal.\n")
    
    run_tree_manipulation(subgoal_resources["behaviors"], subgoal_resources["sub_tree"], db)
        
         
def display_tree_one_level(node, indent=0,):
    print(" " * indent + node.name)

    if isinstance(node, Sequence):
        if node.children:
            for child in node.children:
                print(f"{Back.GREEN} " * indent + f" -> {child.name}")


def run_tree_manipulation(behavior_library, tree, db):

    try: 

        while True:
            display_tree_one_level(tree)
            user_choice = click.prompt(
                "Would you like to make an change before I begin?",
                show_choices=True,
                type=click.Choice(["y", "n"], case_sensitive=False),
            )

            if user_choice == "y":
                action = click.prompt(
                        "\n1. move an existing node\n"
                        + "2. remove an existing node\n"
                        + "3. add a new node\n"
                        + "Please select an action to perform on the behavior tree",
                        type=click.IntRange(min=1, max=4),
                        show_choices=True,
                    )

                if action == 1:
                    #Select node to be moved
                    selected_node = run_interactive_list(tree.children, mode="select")
                    #Select position of node
                    selected_index = run_interactive_list(tree.children, mode="move", new_behavior=selected_node)
                    #Perform operation
                    
                    remove(selected_node, tree)
                    tree.insert_child(selected_index, selected_node)
                    display_tree_one_level(tree)

                    action_log = {
                        "type": "move_node",
                        "nodes": [
                            {
                                "display_name": selected_node.name,
                            },
                        ],
                        "timestamp": datetime.now().isoformat(),
                    }
                    db["action_history"].append(action_log)
                

                elif action == 2:
                    #Select node to be removed
                    selected_node = run_interactive_list(tree.children, mode="select")
                    #Perform operation
                    remove(selected_node, tree)
                    display_tree_one_level(tree)

                    action_log = {
                        "type": "remove_node",
                        "nodes": [
                            {"display_name": selected_node.name},
                        ],
                        "timestamp": datetime.now().isoformat(),
                    }

                    db["action_history"].append(action_log)

                elif action == 3:

                    #TODO: think about where the new action should originally show up in the list. It's original position could
                    #possible affect participant's decision making


                    #Select node to be add
                    selected_node = run_interactive_list(behavior_library, mode="select")
                    #Select position of node
                    selected_index = run_interactive_list(tree.children, mode="insert", new_behavior=selected_node)
                    #Perform operation
                    tree.insert_child(selected_index, selected_node)

                    display_tree_one_level(tree)

                    action_log = {
                        "type": "add_node",
                        "node": {"name": selected_node.name},
                        "timestamp": datetime.now().isoformat(),
                    }


                    db["action_history"].append(action_log)
            
            else:
                break

    except Exception:
        print(
            "\nAn error has occured during the tree manipulation, the experiment will now end."
        )
        db["error_log"] = traceback.format_exc()

    finally:
        return
    

def run_milestone(subgoal_resources, title, db):

    db["start_time"] = datetime.now().isoformat()
    db["base_subtree"] = serialize_tree(subgoal_resources["sub_tree"])
    db["action_history"] = []


    print(f"\nBot: I am starting the following milestone: {title}\n")

    time.sleep(2)
    #node dictionary has 3 attributes
    # - context
    # - behaviors list
    # - subtree, with children list

    summarize_behaviors_check(subgoal_resources, db)
    
    time.sleep(2)
    print("\nBot: Okay, I will begin.\n")

    for action in subgoal_resources["sub_tree"].children:        
        time.sleep(2)
        print(f"Bot: I am about to {action.name}")
        
        if isinstance(action, Sequence):
            print("Bot: This is a Sequence type node, would you like to see the sub-behaviors of this node?")
        time.sleep(1)
        print(f"Action in progress..")
        print("\n")

    db["final_subtree"] = serialize_tree(subgoal_resources["sub_tree"])
    db["end_time"] = datetime.now().isoformat()

    print(f"Bot: The following milestone has been reached: {title}\n")


def sub_function():
    print("subfunction pressed.")

def run_experiment(db, all_resources, experiment_id):
    # Loop for the actual experiment part, which takes user input to decide which action to take
    print("\nExperiment beginning...\n")


    #TODO: provide some context here about the overall experiment

    for subgoal in all_resources:
        db[experiment_id]["experiment_progression"][subgoal] = {}
        run_milestone(all_resources[subgoal], subgoal, db[experiment_id]["experiment_progression"][subgoal])
        # Check for 'p' key press to pause
        # if keyboard.is_pressed('p'):
        #     print("\nPaused. Running sub-function...")
        #     sub_function()
        #     print("Resuming iteration...")


    return db

app = typer.Typer()


# @app.command()
def main(
    resources_file: Annotated[
        pathlib.Path,
        typer.Argument(
            help="file with the experimental context, behavior tree, and behavior library"
        ),
    ],
    db_file: Annotated[
        pathlib.Path,
        typer.Option(help="file where the experimental results will be written"),
    ] = "db.json",
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
    debug: Annotated[bool, typer.Option("--debug")] = False,
):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _logger.debug("debug logging")
    elif verbose:
        logging.basicConfig(level=logging.INFO)
        _logger.debug("verbose logging")
    else:
        logging.basicConfig()

    print("AIT Prototype #1 Simulator")

    # TODO: write up some context, assumptions made in the README

    db = load_db(db_file)

    # load tree to run experiment on, and behavior library

    all_resources = load_resources(resources_file)
    # print(f"\nContext of this experiment: {context_paragraph}")
    
    participant_id, experiment_id = experiment_setup(db)
    
    #TODO: update the colors of the instructions in the prompt toolkit, change the color
    #when we move from first to second interface
    db = run_experiment(db, all_resources, experiment_id)

    save_db(db, db_file)

    # TODO: define export file, that will be where we export the results to
    # TODO: Add more context to simulation ending
    print("\nSimulation has ended.")

    # TODO: visualize the differences between old and new behavior trees after experiment.
    # Potentially use git diff


if __name__ == "__main__":
    main()
