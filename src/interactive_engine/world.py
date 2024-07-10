import random
from dataclasses import dataclass, field, replace
from functools import partial
from pprint import pprint
from time import sleep
from typing import List, Optional, Dict, Any

from interactive_engine.container import take, put, Container
from interactive_engine.engine import Entity, get_attributes, ability
from interactive_engine.lock import make_key, Lock


@dataclass
class World:
    entities: List["Entity"] = field(default_factory=list)


@dataclass
class LocationWorld(World):
    locations: List[Any] = field(default_factory=list)


def init_world():

    robot = Entity(
        name="robot",
        attributes=[],
        abilities=[take, put],
    )

    medicine = Entity("medicine")
    cabinet = Container(name="cabinet", attributes=[medicine])
    world = World(entities=[robot, cabinet])

    tick = partial(sleep, 1)
    return world, tick


if __name__ == "__main__":
    world, tick = init_world()
    pprint(world)
    for i in range(10):
        tick()
        pprint(world)
