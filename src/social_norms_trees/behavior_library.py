class BehaviorLibrary:
    def __init__(self, behavior_list):
        self.behaviors = behavior_list 
        self.behavior_from_display_name = {behavior["display_name"]: behavior for behavior in behavior_list}
        self.behavior_from_id = {behavior["id"]: behavior for behavior in behavior_list}
        
    def get_behavior_by_display_name(self, display_name):
        return self.behaviors.get(display_name)

    def get_behavior_by_id(self, id_):
        for behavior in self.behaviors.values():
            if behavior.id == id_:
                return behavior
        return None