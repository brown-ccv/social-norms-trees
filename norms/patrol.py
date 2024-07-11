import random
from dataclasses import dataclass
from pprint import pprint

import py_trees

from interactive_engine.engine import Entity
from interactive_engine.world import LocationWorld

world = LocationWorld()


@dataclass
class Location:
    name: str


for location in map(lambda x: Location(x), ["wetland", "prarie", "forest"]):
    world.locations.append(location)


travel_functions = []
for location in world.locations:

    def _function(self):
        print(f"go to {location.name}")
        if random.random() > 0.7:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.RUNNING

    _function.__name__ = f"go to {location.name}"
    travel_functions.append(_function)

tree = py_trees.composites.Sequence(
    name="Patrol sequence",
    memory=False,
    children=[],
)


for f in travel_functions:
    tree.add_child(py_trees.meta.create_behaviour_from_function(f)())


@dataclass
class PyTreesAgency:
    tree: py_trees.behaviour.Behaviour


if __name__ == "__main__":
    robot = Entity(
        name="",
        attributes=[PyTreesAgency(tree), random.choice(world.locations)],
    )

    pprint(robot)
    print(py_trees.display.unicode_tree(tree))
    tree.tick_once()
    print(py_trees.display.unicode_tree(tree))
    tree.tick_once()
    print(py_trees.display.unicode_tree(tree))
