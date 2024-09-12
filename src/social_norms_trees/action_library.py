class BehaviorLibrary:
    def __init__(self):
        self.behaviors = {
            "Behavior A": {
                "id": "001",
                "nickname": "Behavior A",
                "type": "Dummy",
            },
            "Behavior B": {
                "id": "002",
                "nickname": "Behavior B",
                "type": "Dummy",
            },
            "Behavior C": {
                "id": "003",
                "nickname": "Behavior C",
                "type": "Dummy",
            },
            "Behavior D": {
                "id": "004",
                "nickname": "Behavior D",
                "type": "Dummy",
            },
            "Behavior E": {
                "id": "005",
                "nickname": "Behavior E",
                "type": "Dummy",
            },
            "Behavior F": {
                "id": "006",
                "nickname": "Behavior F",
                "type": "Dummy",
            },
            "Behavior G": {
                "id": "007",
                "nickname": "Behavior G",
                "type": "Dummy",
            },
            "Behavior H": {
                "id": "008",
                "nickname": "Behavior H",
                "type": "Dummy",
            },

            # these will be the new behaviors that will be possible to "add"
            # as part of new action4 , "add node"
            # TODO: for now, show all actions, and user will just choose the new acton to add

            "Behavior I": {
                "id": "009",
                "nickname": "Behavior I",
                "type": "Dummy",
            },
            "Behavior J": {
                "id": "010",
                "nickname": "Behavior J",
                "type": "Dummy",
            },
            "Behavior K": {
                "id": "011",
                "nickname": "Behavior K",
                "type": "Dummy",
            },
        }

    def get_behavior_by_nickname(self, nickname):
        return self.behaviors.get(nickname)

    def get_behavior_by_id(self, id):
        for behavior in self.behaviors.values():
            if behavior.id == id:
                return behavior
        return None