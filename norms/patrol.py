from dataclasses import dataclass
from pprint import pprint

import py_trees

from interactive_engine.engine import Entity
from interactive_engine.world import LocationWorld

tree = py_trees.composites.Sequence(
    name="Sequence",
    memory=False,
    children=[],
)

world = LocationWorld(locations=["wetland", "prarie", "forest"])


for location in world.locations:

    def _function():
        print(f"go to {location}")

    _function.__name__ = f"go to {location}"
    tree.add_child(py_trees.meta.create_behaviour_from_function(_function)())


@dataclass
class PyTreesAgency:
    tree: py_trees.behaviour.Behaviour


if __name__ == "__main__":
    robot = Entity(name="", attributes=[PyTreesAgency(tree)])
    pprint(robot)
    print(py_trees.display.unicode_tree(tree))
