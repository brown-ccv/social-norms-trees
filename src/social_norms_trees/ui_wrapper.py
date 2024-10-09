import logging
import pathlib
from typing import Annotated, List
import click
from datetime import datetime
import json
import os
import uuid
import py_trees
import traceback

import typer

from social_norms_trees.atomic_mutations import (
    QuitException,
    exchange,
    insert,
    move,
    mutate_chooser,
    remove,
    end_experiment,
)
from social_norms_trees.serialize_tree import deserialize_library_element, serialize_tree, deserialize_tree

from social_norms_trees.behavior_library import BehaviorLibrary

_logger = logging.getLogger(__name__)


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


def experiment_setup(db, origin_tree):
    print("\n")
    participant_id = participant_login()

    experiment_id = initialize_experiment_record(
        db, participant_id, origin_tree)

    print("\nSetup Complete.\n")

    return participant_id, experiment_id


def participant_login():
    participant_id = click.prompt("Please enter your participant id", type=str)

    return participant_id


def load_resources(file_path):
    try:
        print(
            f"\nLoading behavior tree and behavior library from {file_path}...\n")
        with open(file_path, "r") as file:
            resources = json.load(file)

    except json.JSONDecodeError:
        raise ValueError("Error")
    except Exception:
        raise RuntimeError("Error")

    behavior_tree = resources.get("behavior_tree")
    behavior_list = resources.get("behavior_library")
    context_paragraph = resources.get("context")

    behavior_tree = deserialize_tree(
        behavior_tree, BehaviorLibrary(behavior_list))

    behavior_library = [deserialize_library_element(e) for e in behavior_list]

    print("Loading success.")
    return behavior_tree, behavior_library, context_paragraph


def initialize_experiment_record(db, participant_id, origin_tree):
    experiment_id = str(uuid.uuid4())

    # TODO: look into python data class

    experiment_record = {
        "experiment_id": experiment_id,
        "participant_id": participant_id,
        "base_behavior_tree": serialize_tree(origin_tree),
        "start_date": datetime.now().isoformat(),
        "action_history": [],
    }

    db[experiment_id] = experiment_record

    return experiment_id


def display_tree(tree):
    print(py_trees.display.ascii_tree(tree))
    return


def serialize_function_arguments(args):
    results = {}
    if isinstance(args, dict):
        for key, value in args.items():
            results[key] = serialize_function_arguments(value)
        return results
    elif isinstance(args, py_trees.behaviour.Behaviour):
        value = serialize_tree(args, include_children=False)
        return value
    elif isinstance(args, tuple):
        value = tuple(serialize_function_arguments(i) for i in args)
        return value
    elif isinstance(args, list):
        value = [serialize_function_arguments(i) for i in args]
        return value
    else:
        return args


def run_experiment(tree, library):
    # Loop for the actual experiment part, which takes user input to decide which action to take
    print("\nExperiment beginning...\n")

    results_dict = {
        "start_time": datetime.now().isoformat(),
        "initial_behavior_tree": serialize_tree(tree),
        "action_log": []
    }

    try:
        while True:
            display_tree(tree)
            f = mutate_chooser(insert, move, exchange, remove, end_experiment)
            if f is end_experiment:
                break
            results = f(tree, library)
            results_dict["action_log"].append({
                "type": results.function.__name__,
                "kwargs": serialize_function_arguments(results.kwargs),
                "time": datetime.now().isoformat(),
            })

    except QuitException:
        pass

    except Exception:
        print(
            "\nAn error has occured during the experiment, the experiment will now end."
        )
        results_dict["error_log"] = traceback.format_exc()

    # finally:
    results_dict["final_behavior_tree"] = serialize_tree(tree)
    results_dict["start_time"] = datetime.now().isoformat()

    return results_dict


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
        typer.Option(
            help="file where the experimental results will be written"),
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

    original_tree, behavior_library, context_paragraph = load_resources(
        resources_file)
    print(f"\nContext of this experiment: {context_paragraph}")

    participant_id, experiment_id = experiment_setup(db, original_tree)
    results = run_experiment(original_tree, behavior_library)
    db[experiment_id] = results
    _logger.debug(db)
    save_db(db, db_file)

    # TODO: define export file, that will be where we export the results to

    print("\nSimulation has ended.")

    # TODO: visualize the differences between old and new behavior trees after experiment.
    # Potentially use git diff


if __name__ == "__main__":
    app()
