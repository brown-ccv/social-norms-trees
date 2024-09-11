import py_trees

class CustomAction(py_trees.behaviours.Dummy):
    def __init__(self, name, id, nickname):
        super().__init__(name)
        self.id = id
        self.nickname = nickname