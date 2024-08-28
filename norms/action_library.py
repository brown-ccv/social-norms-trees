import py_trees

#Sample action library v1

action_library_1 = {
    "hospital_context": {
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
    "hospital_context": {
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
hospital_context = [1,2,3]
additional_actions = [4,5,6,7]


#Sample action library v3
class Node:
    def __init__(self, name, type):
        self.name = name
        self.taskType = type
    
    def displayName(self):
        print(self.name)

class ActionNode(Task):
    def __init__(self, name):
        super().__init__(name, "action")

class ConditionalNode(Task):
    def __init__(self, name, condition):
        super().__init__(name, "conditional")
        self.condition = condition


open_door = ActionNode("Open Door")
grab_container = ActionNode("Grab Container")
battery_check = ConditionalNode("Check Battery", True)

class NodeLibrary:
    def __init__(self):
        self.actions = []
        self.conditionals = []
        self.composites = []
        self.decorators = []
    
    def add_action_node(self, task):
        self.actions.append(task)
    
    def add_conditional_node(self, task):
        self.conditionals.append(task)
    
    def get_task_by_type(self, type):
        if type.lower() == "action":
            return self.actions
        elif type.lower() == "conditional":
            return self.conditionals
        elif type.lower() == "composite":
            return self.composites
        elif type.lower() == "decorator":
            return self.decorators
        else:
            return

#Four types of tasks 
# - action
#   - alter the state of the game in some way
#   - Ex. open door
#   - Ex. grab container

# - conditional
#   - test some property of the game
#   - Ex. check the robot battery % 
#   - Ex. check if patient is in the room
#   - Paired with action task, only run action task if conditional task is true


# - composite
#   - a parent task that holds a list of child tasks. 
#   - Sequence and parallel tasks are both composite
#   - Sequence = run each task once until all tasks have been run
#   - Parallel = run all children tasks at the same time


# - decorator
#   - a parent task that can only have one child
#   - function is to modify the behavior of the child task
