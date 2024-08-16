import py_trees

#Sample action library v1

action_library_1 = {
    "test_tree_1": {
        "approach_door": py_trees.behaviours.Dummy(name="approach_door"),
        "open_door": py_trees.behaviours.Dummy(name="open_door"),
        "go_through_door": py_trees.behaviours.Dummy(name="go_through_door"),
    },
    "additional_actions": {
        "knock_on_door": py_trees.behaviours.Dummy(name="knock_on_door"),
        "sound_siren": py_trees.behaviours.Dummy(name="sound_siren"),
        "turn_around": py_trees.behaviours.Dummy(name="turn_around"),
        "wait_for_answer": py_trees.behaviours.Dummy(name="wait_for_answer"),
    }
}


#Sample action library v2

action_library_2 = {
    "test_tree_1": {
        1: "approach_door",
        2: "open_door",
        3: "go_through_door",
    },
    "additional_actions": {
        1: "knock_on_door",
        2: "sound_siren",
        3: "turn_around",
        4: "wait_for_answer",
    }
}


#Sample action library v3

action_library_3 = {
    1: "approach_door",
    2: "open_door",
    3: "go_through_door",
    4: "knock_on_door",
    5: "sound_siren",
    6: "turn_around",
    7: "wait_for_answer",
}
test_tree_1 = [1,2,3]
additional_actions = [4,5,6,7]


