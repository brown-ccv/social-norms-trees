import time
import click
from datetime import datetime
import json

# Global database
db = {}

def experiment_setup():

    print("\n")
    participant_id = participant_login()

    print("\n")
    origin_tree = load_behavior_tree()

    experiment_id = initialize_experiment_record(participant_id, origin_tree)

    print("\nSetup Complete.\n")

    return participant_id, origin_tree, experiment_id

def participant_login():
    global db

    participant_id = click.prompt("Please enter your participant id", type=str)

    if participant_id not in db:
        db[participant_id] = {}

    return participant_id



def get_behavior_trees():
    #TODO: Get behavior trees from respective data structure

    print("1. Original Tree")

    return ["Original_tree"]

def load_behavior_tree():
    
    tree_array = get_behavior_trees()
    tree_index = click.prompt("Please select a behavior tree to load for the experiment (enter the number)", type=int)
    return tree_array[tree_index - 1]



def initialize_experiment_record(participant_id, origin_tree):
    global db

    if "experiments" not in db[participant_id]:
        db[participant_id]["experiments"] = {}

    experiment_id = len(db[participant_id]["experiments"]) + 1

    experiment_record = {
        "experiment_id": experiment_id,
        "base_behavior_tree": origin_tree,
        "start_date": datetime.now().isoformat(),
        "actions": [],
    }

    db[participant_id]["experiments"][experiment_id] = experiment_record

    return experiment_id


def run_experiment(participant_id, origin_tree, experiment_id):
    global db

    #TODO: run actual experiment
    print("Running experiment...\n")
    db[participant_id]["experiments"][experiment_id]["final_behavior_tree"] = "updated tree"
    db[participant_id]["experiments"][experiment_id]["actions"] = ["list", "of", "actions"]
    time.sleep(3)
    db[participant_id]["experiments"][experiment_id]["end_date"] = datetime.now().isoformat()
    print("Experiment done!\n")





def main():

    print("AIT Prototype #1 Simulator")

    for _ in range(3):
        participant_id, origin_tree, experiment_id = experiment_setup()
        run_experiment(participant_id, origin_tree, experiment_id)
        print(json.dumps(db, indent=4))
    

if __name__ == "__main__":
    main()