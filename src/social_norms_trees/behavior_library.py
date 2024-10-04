class BehaviorLibrary:
    def __init__(self, behavior_list):
        self.behaviors = behavior_list
        self.behavior_from_display_name = {
            behavior["display_name"]: behavior for behavior in behavior_list
        }
        self.behavior_from_id = {
            behavior["id"]: behavior for behavior in behavior_list}
