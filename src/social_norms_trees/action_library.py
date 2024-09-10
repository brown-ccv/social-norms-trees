class ActionLibrary:
    def __init__(self):
        self.actions = {
            "Action A": {
                "id": "001",
                "nickname": "Action A",
                "type": "Dummy",
            },
            "Action B": {
                "id": "002",
                "nickname": "Action B",
                "type": "Dummy",
            },
            "Action C": {
                "id": "003",
                "nickname": "Action C",
                "type": "Dummy",
            },
            "Action D": {
                "id": "004",
                "nickname": "Action D",
                "type": "Dummy",
            },
            "Action E": {
                "id": "005",
                "nickname": "Action E",
                "type": "Dummy",
            },
            "Action F": {
                "id": "006",
                "nickname": "Action F",
                "type": "Dummy",
            },
            "Action G": {
                "id": "007",
                "nickname": "Action G",
                "type": "Dummy",
            },
            "Action H": {
                "id": "008",
                "nickname": "Action H",
                "type": "Dummy",
            },

            "Action I": {
                "id": "009",
                "nickname": "Action I",
                "type": "Dummy",
            },
            "Action J": {
                "id": "010",
                "nickname": "Action J",
                "type": "Dummy",
            },
            "Action K": {
                "id": "011",
                "nickname": "Action K",
                "type": "Dummy",
            },
        }

    def get_action_by_nickname(self, nickname):
        return self.actions.get(nickname)

    def get_action_by_id(self, id):
        for action in self.actions.values():
            if action.id == id:
                return action
        return None
        


# "base_behavior_tree": {
#     "name": "Sequence A",
#     "children": [
#         {
#             "name": "Action A",
#             "children": []
#         },
#         {
#             "name": "Action B",
#             "children": []
#         },
#         {
#             "name": "Sequence B",
#             "children": [
#                 {
#                     "name": "Action C",
#                     "children": []
#                 },
#                 {
#                     "name": "Action D",
#                     "children": []
#                 }
#             ]
#         },
#         {
#             "name": "Sequence C",
#             "children": [
#                 {
#                     "name": "Action E",
#                     "children": []
#                 },
#                 {
#                     "name": "Action F",
#                     "children": []
#                 },
#                 {
#                     "name": "Action G",
#                     "children": []
#                 },
#                 {
#                     "name": "Action H",
#                     "children": []
#                 }
#             ]
#         }
#     ]
# },