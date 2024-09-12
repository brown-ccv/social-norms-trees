import py_trees

class CustomBehavior(py_trees.behaviours.Dummy):
    def __init__(self, name, id, nickname):
        super().__init__(name)
        self.id_ = id
        self.nickname = nickname



    # id of the behavior within the behavior library (persists)
    # but also the unique id for the behavior within the tree (in case there are multiple instances of
    # the behavior in one tree)


