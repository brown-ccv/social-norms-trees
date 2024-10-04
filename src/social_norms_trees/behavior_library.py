class BehaviorLibrary:
    def __init__(self, behaviors):
        self.behaviors = behaviors

    def get_behavior_by_nickname(self, nickname):
        return self.behaviors.get(nickname)

    def get_behavior_by_id(self, id_):
        for behavior in self.behaviors.values():
            if behavior.id == id_:
                return behavior
        return None
