# Experiment Resources

This guide provides instructions for creating and structuring resource-file.json, which is used to define the behavior tree and experiment flow for robots. Currently, there are three robots with custom contexts:

1. Atlas
2. Digit
3. Optimus




## Breakdown of {robot}-resource-file.json

Resource files are JSON files made up of key-value pairs. The keys represent subgoals, and their values define the subgoal's context, children, behavior library, and interruptions.

Here’s an example template:


```json
{
    "subgoal_A": {
        "context": "...",
        "children": [],
        "behavior_library": [
            {
                "id": "...",
                "name": "...",
                "in_behavior_bank": false
            },
            {
                "id": "...",
                "name": "...",
                "in_behavior_bank": true
            }
        ],
        "interruptions": {}
    },
    "subgoal_B": {
        "context": "...",
        "children": [],
        "behavior_library": [
            {
                "id": "...",
                "name": "...",
                "in_behavior_bank": false
            },
            {
                "id": "...",
                "name": "...",
                "in_behavior_bank": true
            }
        ],
        "interruptions": {}
    }
}
```

## Subgoal Structure Breakdown
- Each subgoal is represented by a unique key (e.g., "subgoal_A") with the following fields:


### Context
- A string describing the subgoal's background and objectives.

Example:
```json
"context": "Atlas is assigned to retrieve medicine A from the medicine cabinet..."
```


### Children
- An array of behavior IDs (strings) specifying the execution order of the subgoal's behaviors.
- Important: These IDs must exist in the behavior_library field.

Example:
```json
"children": [
    "take_path_to_medicine_cabinet",
    "unlock_cabinet",
    "retrieve_medicine"
]
```


### Behavior Library
- A list of all possible behaviors for the subgoal.
- Each behavior is an object with the following fields:
  - id (required): Unique identifier.
  - name (required): Description of the behavior.
  - in_behavior_bank (optional): true if included in the behavior bank.

Example:
```json
"behavior_library": [
    {
        "id": "take_path_to_medicine_cabinet",
        "name": "take acceptable path to the medicine cabinet",
        "in_behavior_bank": false
    },
    {
        "id": "request_medicine",
        "name": "request medicine from pharmacist",
        "in_behavior_bank": true
    }
]
```

### Interruptions

Currently not used. Keep as an empty object: {}



