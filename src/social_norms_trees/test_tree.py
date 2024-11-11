"""
--- start of simulation ---


Bot: Hello! Are you ready to begin today's experiment? 

Choose option (y/n): y

User: Yes, I am ready. 

Bot: Great! Let's get started. Here is the scenario we will simulate today. 
I am assigned to retrieve and deliver medicine M to patient P in room 405. It is currently on the third floor
near the nurse's desk. The required medicine is located on the third floor, but the patient is on the fourth            <---- present context paragraph
floor. This focal goal triggers a plan with the main components of picking up the medicine, moving to 
the 4th floor, and delivering the medicine 

Bot: Let's get started. 



Bot: I will now attempt to fufill the following milestone: Pick up the medicine                                         <---- present subgoal 1 

Bot: Here are the actions, in order, that I will take to achieve this goal.                                             <---- list out predefined actions for subgoal 1 
1. Take path to medicine cabinet
2. Unlock the cabinet                   
3. Retrieve the medicine

Bot: Shall I proceed? 

Choose option (Continue, Stop): Continue                                                                                <---- participant can 1. allow bot to proceed.
                                                                                                                                              2. stop, and manipulate the predefined set of actions for subgoal 1
User: Yes, let's continue.                                                                                                                    3. stop experiment?
                                                                                                                                              
Bot: Okay, I will begin.                                                                                                                     

Bot: I am now taking the path to the medicine cabinet.
Action in progress...                                                                                                   <---- we can add a slight time delay here for realism

Bot: The action has been completed. I will now proceed on to the next action.                                           <---- action complete confirmation

Bot: I am now unlocking the cabinet. 
Action in progress...

Bot: The action has been completed. I will now proceed on to the next action. 

Bot: I am now retrieving the medicine.
Action in progress...

Bot: The following milestone has been reached: Pick up the medicine                                                    <---- milestone complete confirmation



Bot: I will now attempt to fulfill the following milestone: Get to the 4th floor                                         <---- present subgoal 2                                             
                                                                                                                        *** do we want to have some sort of "subgoal-level" context paragraphs? How does that coexist with interruptions? or are they the same? ***
Bot: Here are the actions, in order, that I will take to achieve this goal.                                             <---- list out predefined actions for subgoal 1 
1. Take an acceptable path to the elevator
2. Get into the elevator
3. Press the correct floor button
4. Exit the elevator

Bot: Shall I proceed? 

Choose option (Continue, Stop): Stop

User: No, stop.

Bot: Okay, I've stopped. What would you like me to do next?

1. Introduce a new action                                                                                               <---- this represents our "mutate tree" actions section
2. Reordering actions                                                                                                   how they a represented can be changed or updated
3. Remove a current action
Choose option: 1 

User: Let's introduce a new action.

Bot: Understood, what action would you like to introduce?

1. Request permission to enter elevator and acts according to the response
Choose option: 1

User: Let's add the following action: Request permission to enter elevator and acts according to the response

Bot: Okay, where should this action go?

{0}
-> Take an acceptable path to the elevator
{1}
-> Get into the elevator
{2}
-> Press the correct floor button
{3}
-> Exit the elevator
{4}
Choose option: 1

User: Let's place it at index: 1 

Bot: Here are the actions, in order, that I will take to achieve this goal.                                             <---- Updated actions with new introduced actions
1. Take an acceptable path to the elevator
2. Request permission to enter elevator and acts according to the response
3. Get into the elevator
4. Press the correct floor button
5. Exit the elevator
Choose option (Continue, Stop): Continue

-- experiment continues.. --

"""




"""
-- interuption module --
While the bot was moving towards the medicine cabinet, it was interrupted by a visitor. "Hello, I'm looking             <---- triggered by storyline
for room 536 to visit John. Can you help me find the way?"

Bot: There has been an interruption. Based on my abilities, I determine I should do the following action
to address the interruption:
"""


#Can actions be broken down into some sort of template?
# 1 Action, 1 Destination or 1 Object or 1 Subject


import time
from dataclasses import dataclass



# @dataclass
# class Behaviour:
#     """Custom class for behavior tree behaviour type nodes"""
#     name: str

#pick up medicine subgoal
# take_path_to_medicine_cabinet = Behaviour("take acceptable path to the medicine cabinet")
# unlock_cabinet = Behaviour("unlock the cabinet")
# retrieve_medicine = Behaviour("retrieve the medicine")

#travel to desired floor subgoal
# take_path_to_elevator = Behaviour("take acceptable path to the elevator")
# get_into_elevator = Behaviour("get into the elevator")
# press_correct_floor_button = Behaviour("press the correct floor button")
# exit_elevator = Behaviour("exit the elevator")

#deliver medicine to patient subgoal
# take_path_to_patient_room = Behaviour("take acceptable path to patient room")
# enter_room = Behaviour("enter the room")
# announce_presence_and_task = Behaviour("announce own presence and task")
# wait_for_permission = Behaviour("wait for permission")
# enter_room = Behaviour("enter room")
# hand_patient_medicine = Behaviour("hand the patient the medicine")




#create dataclasses for behaviours and sequence

@dataclass
class Sequence:
    """Custom class for behavior tree sequence type nodes"""
    name: str
    memory: bool
    children: list



# pick_up_medicine = Sequence(
#     "pick up the medicine",
#     False,
#     [
#         take_path_to_medicine_cabinet,
#         unlock_cabinet,
#         retrieve_medicine
#     ]
# )


# travel_to_desired_floor = Sequence(
#     "travel to desired floor",
#     False,
#     children = [
#         take_path_to_elevator,
#         get_into_elevator,
#         press_correct_floor_button,
#         exit_elevator
#     ]
# )

# deliver_medicine_to_patient_in_room = Sequence(
#     "deliver the medicine to patient inside the patient room",
#     False,
#     children = [
#         take_path_to_patient_room,
#         announce_presence_and_task,
#         wait_for_permission,
#         enter_room,
#         hand_patient_medicine
#     ]
# )


# #root tree
# test_scenario_1 = Sequence(
#     "deliver medicine to the patient",
#     False,
#     children=[
#         pick_up_medicine,
#         travel_to_desired_floor,
#         deliver_medicine_to_patient_in_room
#     ],
# )

#how to incorporate the set of behaviors that are relevant to the experiment? or a specific subtree?

@dataclass
class Interruption:
    """Custom class for behavior tree sequence type nodes"""
    interruption_event: str
    interruption_context: bool

@dataclass
class EnvironmentSimulator:
    """Custom class for behavior tree sequence type nodes"""
    interruptions: dict

class EnvironmentSimulator:
    def __init__(self, interruptions):
        self.interruptions = {interruption.interruption_event: interruption.interruption_context for interruption in interruptions}


interruption1 = Interruption(
    interruption_event="take acceptable path to the medicine cabinet",
    interruption_context="While moving toward the medicine cabinet, the robot is interrupted by a visitor: “Hello, I’m looking for room 536 to visit John. Can you help me find the way?”"
)

interruption2 = Interruption(
    interruption_event="unlock the cabinet",
    interruption_context="Upon reaching the cabinet, the robot finds it locked and is unable to electronically open it with the password."
)


pick_up_medicine_environment = EnvironmentSimulator(
    interruptions=[interruption1, interruption2],
)

class Blackboard:
    def __init__(self):
        self.data = {}

    def set(self, location, values):
        if location not in self.data:
            self.data[location] = {}
        self.data[location].update(values)

    def get(self, location, key):
        return self.data.get(location).get(key)

    def get_location_data(self, location):
        return self.data.get(location)

    def get_all_data(self):
        return self.data

#TODO 11/11:
# May require some set of conditional checks to help the robot determine its "state" and optimal next behaviours
# Define the script's divergence, possibly limit, to control, the limited amount of different scenarios in this specific experiment simulation. 
# we don't let all possible outcomes happen, "guide" the robot to a certain # of outcomes. 
#next small goal. we will try to create a more realistic next prototype. one that focuses still on the separation of tree into multiple subgoals, where the user, guided by the context. will iterate through 
#the simulation. at each point they can make adjustments. Eventually, we will export all fo this in some way. 

class RobotState:
    def __init__(self, time=None, floor=None, room=None, task=None,subgoal=None, inventory=None, presence=None, role=None):
        # Initialize state attributes

        #time of day
        self.time = time
        #robot's room location
        self.room = room
        #robot's floor location
        self.floor = floor
        #robot's overall task
        self.task = task
        #robot's current subgoal
        self.subgoal = subgoal
        #items in the robot's inventory
        self.inventory = inventory
        #presence of individuals in the robot's vincinity
        self.presence = presence
        #robot's role, robot's abilities?
        self.role = role


    def update_field(self, field_name, new_value):
        setattr(self, field_name, new_value)


    def get_status_report(self):
        return {
            "time": self.time,
            "room": self.room,
            "floor": self.floor,
            "task": self.task,
            "subgoal": self.subgoal,
            "inventory": self.inventory,
            "presence": self.presence,
            "role": self.role
        }
    
    def execute_behaviour(self, behaviour):
        if behaviour.state_update_function:
            behaviour.state_update_function(self)




#keyboard interrupts, typer and click you can get keyboard interrupts. by throwing exceptions

def run_experiment(node):
    print(f"Starting the following experiment: {node.name}\n")

    #initialize robot state with initial location and initial robot status 
    robot_state = RobotState(
        time="afternoon",
        room="A",
        floor="3")

    
    #initialize blackboard with all room/location statuses
    blackboard = Blackboard()

    blackboard.set("elevator", {
        "status": "available",
        "occupants": 2,
        "max_occupants": 4
    })

    blackboard.set("room 405", {
        "door_status": "locked",
        "occupants": 1, 
        "max_occupants": 4
    })

    blackboard.set("medicine_cabinet", {
        "door_status": "unlocked",
        "occupants": 0, 
        "max_occupants": 4,
        "inventory": {"painkillers": 10, "antibiotics": 5}
    })

        
    for child in node.children:
        print(robot_state.get_status_report())

        time.sleep(2)
        print(f"\nBot: I am starting the following milestone: {child.name}\n")
        robot_state.update_field("subgoal", child.name)
        run_milestone(child, robot_state)


def run_milestone(node, robot_state):
    time.sleep(2)
    # print("Bot: Here are the actions, in order, that I will take to achieve this goal.")
    # for index, action in enumerate(node.children):
    #     print(f"{index}: {action.name}")
    # time.sleep(2)
    print("\nBot: Okay, I will begin.\n")

    for behaviour in node.children:        
        time.sleep(2)
        print(f"Bot: I am {behaviour.name}")
        robot_state.execute_behaviour(behaviour)
        print(robot_state.get_status_report())
        time.sleep(1)

        # print(f"Action in progress..")

        #check for interruption
        # if action.name in pick_up_medicine_environment.interruptions.keys():
        #     print("-- interruption --")
        #     print(pick_up_medicine_environment.interruptions[action.name])
        # print("\n")

    print(f"Bot: The following milestone has been reached: {node.name}\n")
# Start traversal from the root of the tree
# run_experiment(test_scenario_1)


#think about the blackboard, how to incorporate
# Bertram wants contexts to be made of:
# Time (because different times of day you might have different norms)
# Space (e.g. patients room, between rooms, office door)
# Task (e.g. deliver lunch, deliver medicine – urgency)
# Presence of other people (e.g. is there a physician, family member, is the patient there?)
# Role (e.g. nurse assistant robot vs mechanic robot) 
# potential categorizing these for the robot in the blackboard




from enum import Enum
from typing import Optional, Callable



# action words
# - take, enter, walk, exit, wait (lower body/foot movement) + destination or source (location)
# - unlock, lock, press, retrieve, pickup, let go (upper body/arm movement) + object 
# - alert, announce, reject, request, ask (sound/voice) + subject (individual, group) 



# subjects (in this context)
# nurse, patient, doctor, security, visitor, 


# object (in this context)
# medicine, cabinet, key, elevator button


# destinations
# fourth floor, elevator, medicine cabinet, patient room 405, patient room 536




class ActionType(Enum):
    MOVEMENT = "movement"
    OPERATION = "operation"
    COMMUNICATION = "communication"

class TargetType(Enum):
    DESTINATION = "destination"
    OBJECT = "object"
    SUBJECT = "subject"

@dataclass
class Behaviour:
    id: str
    name: str
    action_type: ActionType
    action: str
    target_type: TargetType
    target: str
    state_update_function: Optional[Callable[[RobotState], None]] = None


a1 = Behaviour(id="take_path_to_elevator", 
       name="take acceptable path to the elevator lobby", 
       action_type=ActionType.MOVEMENT, 
       action="take", 
       target_type=TargetType.DESTINATION,
       target="elevator lobby",
       state_update_function=lambda robot_state: setattr(robot_state, "room", "elevator lobby")
       )


a2 = Behaviour(id="get_into_elevator", 
        name="get into the elevator", 
        action_type=ActionType.MOVEMENT, 
        action="get into", 
        target_type=TargetType.DESTINATION,
        target="elevator",
        state_update_function=lambda robot_state: setattr(robot_state, "room", "elevator")
       )


a3 = Behaviour(id="press_correct_floor_button", 
        name="press the correct floor button", 
        action_type=ActionType.OPERATION, 
        action="press", 
        target_type=TargetType.OBJECT,
        target="correct floor button",
        state_update_function=lambda robot_state: setattr(robot_state, "floor", "4")
       )

a4 = Behaviour(id="alert_adminstrator", 
       name="alert administrator for assistance", 
       action_type=ActionType.COMMUNICATION, 
       action="alert", 
       target_type=TargetType.SUBJECT,
       target="administrator",
       )


pick_up_medicine = Sequence(
    "pick up the medicine",
    False,
    children=[
        a1,
        a2,
        a3
    ]
)


test_scenario_1 = Sequence(
    "deliver medicine to the patient",
    False,
    children=[
        pick_up_medicine
    ]
)


run_experiment(test_scenario_1)



#based on target_type, we will make some sort of update to robotstate.
# if action_type = movement and target_type = destination, we will update the space. 


#Blackboard 







#One other idea, do we have the user "build" the action? 
# or it could simply be about using the action type and target type to "rate" the effectiveness of the current action
# for example. The robot is on floor 3, it already has the medicine and so the logical thing is for the robot to now travel to floor 4. 
# knowing this context of floor, vs current motive, we can differentiate doing a "OPERATION" action vs "MOVEMENT" action. it is more 
# logical to do the movement, vs the operation. This is how the robot will be "aware" of its surroundings


# especially for the context driven changes, or interruptions, what is "correct" is really defined by the user. How they all decide what
# the robot does. We are the initial arbiter, but of course we cannot anticipate and predict all of the scenarios, so there will be 
# some scenarios that will have to be defined by converged user data

# how do we "simulate" that scenario, where we don't have a written out outcome of what happens after certain actions. We may really
# have to look into the context, and see how actions, and string of actions lead the robot to what sort of results. 
# meaning, we may have to incorporate how we can "rate" or "determine" the robot's status in this simulated world, and essentially, build 
# a virtual environment out of this, determine if robot is currently successful or totally incorrect. 





#Location
# Start on third floor near the nurse's desk. 

# medicine cabinet = third floor

# patient room = fourth floor


'''
Bot: Attempting to Enter the elevator
Precondition not met for: Enter the elevator
Bot: Could not perform action 'Enter the elevator' due to unmet conditions. (all because elevator_status = full)
'''