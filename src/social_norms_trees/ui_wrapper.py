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

from social_norms_trees.behaviour_tree_library import Behaviour, Sequence


from social_norms_trees.atomic_mutations import (
    QuitException,
    exchange,
    insert,
    move,
    mutate_chooser,
    remove,
    end_experiment,
)
from social_norms_trees.serialize_tree import serialize_tree, deserialize_tree



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


def experiment_setup(db):
    print("\n")
    participant_id = participant_login()

    experiment_id = initialize_experiment_record(db, participant_id)

    print("\nSetup Complete.\n")

    return participant_id, experiment_id


def participant_login():
    participant_id = click.prompt("Please enter your participant id", type=str)

    return participant_id




def deserialize_behaviours(behaviours):
    deserialized_behaviours = {}

    for behaviour in behaviours:
        deserialized_behaviours[behaviour["id"]] = Behaviour(id=behaviour["id"], name=behaviour["name"])

    return deserialized_behaviours

def build_tree(context, children, behaviours):
    
    children_behaviours = []
    
    parent_node = Sequence(
        name=context,
        memory=False,
    )

    for behaviour_id in children:
        behaviours[behaviour_id].parent = parent_node
        children_behaviours.append(behaviours[behaviour_id])
    
    return Sequence(
        name=context,
        memory=False,
        children= children_behaviours
    )

        
def display_tree(node, indent=0):
    """Recursively display the behavior tree in a readable format."""
    if isinstance(node, Sequence):
        print(" " * indent + node.name)
        if node.children:
            for child in node.children:
                display_tree(child, indent + 4)
    elif isinstance(node, Behaviour):
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
        behaviour_list = resources[subtree].get("behaviour_library")
        context_paragraph = resources[subtree].get("context")

        #deserialize behavior_list
        behaviours = deserialize_behaviours(behaviour_list)
        
        #then use it to build the subgoal behavior tree
        sub_tree = build_tree(context_paragraph, children, behaviours)

        all_resources[subtree] = {
            "context": context_paragraph,
            "behaviours": behaviours,
            "sub_tree": sub_tree
        }
       
    return all_resources

def initialize_experiment_record(db, participant_id):
    experiment_id = str(uuid.uuid4())

    # TODO: look into python data class

    experiment_record = {
        "experiment_id": experiment_id,
        "participant_id": participant_id,
        "start_date": datetime.now().isoformat(),
        "action_history": [],
    }

    db[experiment_id] = experiment_record

    return experiment_id

def summarize_behaviours_check(subgoal_resources):
    print("Bot: Here are the actions, in order, that I will take to achieve this goal.")
    for index, action in enumerate(subgoal_resources["sub_tree"].children):
        print(f"{index}: {action.name}")
    
    print("Bot: Shall I proceed?")
    user_choice = click.prompt(
                "Choose option",
                show_choices=True,
                type=click.Choice(["Continue", "Stop"], case_sensitive=False),
            )

    if user_choice == "Stop":
        run_tree_manipulation(subgoal_resources["behaviours"], subgoal_resources["sub_tree"])
        
            

def run_tree_manipulation(behaviour_library, tree):
    display_tree(tree)

    print("done.")



    # try:
    #     while True:
    #         print(py_trees.display.ascii_tree(origin_tree))
    #         user_choice = click.prompt(
    #             "Would you like to perform an action on the behavior tree?",
    #             show_choices=True,
    #             type=click.Choice(["y", "n"], case_sensitive=False),
    #         )

    #         if user_choice == "y":
    #             action = click.prompt(
    #                 "1. move node\n"
    #                 + "2. exchange node\n"
    #                 + "3. remove node\n"
    #                 + "4. add node\n"
    #                 + "Please select an action to perform on the behavior tree",
    #                 type=click.IntRange(min=1, max=4),
    #                 show_choices=True,
    #             )

    #             if action == 1:
    #                 origin_tree, action_log = move_node(origin_tree)
    #                 db[experiment_id]["action_history"].append(action_log)
    #             elif action == 2:
    #                 origin_tree, action_log = exchange_nodes(origin_tree)
    #                 db[experiment_id]["action_history"].append(action_log)

    #             elif action == 3:
    #                 origin_tree, action_log = remove_node(origin_tree)
    #                 db[experiment_id]["action_history"].append(action_log)

    #             elif action == 4:
    #                 origin_tree, action_log = add_node(origin_tree, behavior_library)
    #                 db[experiment_id]["action_history"].append(action_log)

    #             else:
    #                 print(
    #                     "Invalid choice, please select a valid number (1, 2, 3, or 4).\n"
    #                 )

    #         # user_choice == "n", end simulation run
    #         else:
    #             break

    # except Exception:
    #     print(
    #         "\nAn error has occured during the experiment, the experiment will now end."
    #     )
    #     db[experiment_id]["error_log"] = traceback.format_exc()

    # finally:
    #     db[experiment_id]["final_behavior_tree"] = serialize_tree(origin_tree)
    #     db[experiment_id]["end_date"] = datetime.now().isoformat()
    #     return db
    

def run_milestone(subgoal_resources, title):
    print(f"\nBot: I am starting the following milestone: {title}\n")

    time.sleep(2)
    #node dictionary has 3 attributes
    # - context
    # - behaviours list
    # - subtree, with children list

    summarize_behaviours_check(subgoal_resources)
    
    time.sleep(2)
    print("\nBot: Okay, I will begin.\n")

    for action in subgoal_resources["sub_tree"].children:        
        time.sleep(2)
        print(f"Bot: I am {action.name}")
        time.sleep(1)
        print(f"Action in progress..")
        print("\n")

    print(f"Bot: The following milestone has been reached: {title}\n")



def run_experiment(db, all_resources, experiment_id):
    # Loop for the actual experiment part, which takes user input to decide which action to take
    print("\nExperiment beginning...\n")

    for subgoal in all_resources:
        run_milestone(all_resources[subgoal], subgoal)


app = typer.Typer()


@app.command()
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
    db = run_experiment(db, all_resources, experiment_id)
    # save_db(db, db_file)

    # TODO: define export file, that will be where we export the results to

    print("\nSimulation has ended.")

    # TODO: visualize the differences between old and new behavior trees after experiment.
    # Potentially use git diff


if __name__ == "__main__":
    app()
