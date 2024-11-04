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
2. Reorder a current action                                                                                                   how they a represented can be changed or updated
3. Exchange two actions                                                                                                       for now, represents the update robot actions module
4. Remove a current action
5. End Experiment
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



@dataclass
class Behaviour:
    """Custom class for behavior tree behaviour type nodes"""
    name: str

#pick up medicine subgoal
take_path_to_medicine_cabinet = Behaviour("take acceptable path to the medicine cabinet")
unlock_cabinet = Behaviour("unlock the cabinet")
retrieve_medicine = Behaviour("retrieve the medicine")

#travel to desired floor subgoal
take_path_to_elevator = Behaviour("take acceptable path to the elevator")
get_into_elevator = Behaviour("get into the elevator")
press_correct_floor_button = Behaviour("press the correct floor button")
exit_elevator = Behaviour("exit the elevator")

#deliver medicine to patient subgoal
take_path_to_patient_room = Behaviour("take acceptable path to patient room")
enter_room = Behaviour("enter the room")
announce_presence_and_task = Behaviour("announce own presence and task")
wait_for_permission = Behaviour("wait for permission")
enter_room = Behaviour("enter room")
hand_patient_medicine = Behaviour("hand the patient the medicine")




#create dataclasses for behaviours and sequence

@dataclass
class Sequence:
    """Custom class for behavior tree sequence type nodes"""
    name: str
    memory: bool
    children: list



pick_up_medicine = Sequence(
    "pick up the medicine",
    False,
    [
        take_path_to_medicine_cabinet,
        unlock_cabinet,
        retrieve_medicine
    ]
)


travel_to_desired_floor = Sequence(
    "travel to desired floor",
    False,
    children = [
        take_path_to_elevator,
        get_into_elevator,
        press_correct_floor_button,
        exit_elevator
    ]
)

deliver_medicine_to_patient_in_room = Sequence(
    "deliver the medicine to patient inside the patient room",
    False,
    children = [
        take_path_to_patient_room,
        announce_presence_and_task,
        wait_for_permission,
        enter_room,
        hand_patient_medicine
    ]
)


#root tree
test_scenario_1 = Sequence(
    "deliver medicine to the patient",
    False,
    children=[
        pick_up_medicine,
        travel_to_desired_floor,
        deliver_medicine_to_patient_in_room
    ],
)

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
    context="While moving toward the medicine cabinet, the robot is interrupted by a visitor: “Hello, I’m looking for room 536 to visit John. Can you help me find the way?”"
)

interruption2 = Interruption(
    interruption_event="unlock the cabinet",
    context="Upon reaching the cabinet, the robot finds it locked and is unable to electronically open it with the password."
)


pick_up_medicine_environment = EnvironmentSimulator(
    interruptions=[interruption1, interruption2],
)

#keyboard interrupts, typer and click you can get keyboard interrupts. by throwing exceptions

def run_experiment(node):
    print(f"Starting the following experiment: {node.name}\n")

    for child in node.children:
        time.sleep(2)
        print(f"\nBot: I am starting the following milestone: {child.name}\n")
        run_milestone(child)


def run_milestone(node):
    time.sleep(2)
    print("Bot: Here are the actions, in order, that I will take to achieve this goal.")
    for index, action in enumerate(node.children):
        print(f"{index}: {action.name}")
    time.sleep(2)
    print("\nBot: Okay, I will begin.\n")

    for action in node.children:        
        time.sleep(2)
        print(f"Bot: I am {action.name}")
        time.sleep(1)
        print(f"Action in progress..")

        #check for interruption
        if action.name in pick_up_medicine_environment.interruptions.keys():
            print("-- interruption --")
            print(pick_up_medicine_environment.interruptions[action.name])
        print("\n")

    print(f"Bot: The following milestone has been reached: {node.name}\n")
# Start traversal from the root of the tree
run_experiment(test_scenario_1)


#think about the blackboard, how to incorporate
# Bertram wants contexts to be made of:
# Time (because different times of day you might have different norms)
# Space (e.g. patients room, between rooms, office door)
# Task (e.g. deliver lunch, deliver medicine – urgency)
# Presence of other people (e.g. is there a physician, family member, is the patient there?)
# Role (e.g. nurse assistant robot vs mechanic robot) 
#potentiall categorizing these for the robot in the blackboard
