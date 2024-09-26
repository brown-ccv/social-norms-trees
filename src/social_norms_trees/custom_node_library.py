import py_trees

class CustomBehavior(py_trees.behaviours.Dummy):
    def __init__(self, name, id_, display_name):
        super().__init__(name)
        self.id_ = id_
        self.display_name = display_name


class CustomSequence(py_trees.composites.Sequence):
    def __init__(self, name, id_, display_name, children=None, memory=False):
        super().__init__(name=name, memory=memory)
        self.id_ = id_
        self.display_name = display_name
        
        if children:
            self.add_children(children)


    # id of the behavior within the behavior library (persists)
    # but also the unique id for the behavior within the tree (in case there are multiple instances of
    # the behavior in one tree)


