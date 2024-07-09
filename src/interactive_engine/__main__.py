import curses
import inspect
import random
from dataclasses import dataclass, field
from pprint import pprint, pformat
from time import sleep
from typing import Sequence, List, Any, Optional, Union


@dataclass
class World():
    landscape: str
    entities: List["Entity"]

@dataclass
class Entity():
    name: str
    representation: str
    attributes: List[Union["Entity", dataclass]] = field(default_factory=list)
    abilities: List[Any] = field(default_factory=list)


def ability(f):
    """Decorator for abilities."""
    first_argument_type = next(iter(inspect.signature(f).parameters.values())).annotation

    def inner(e, *args, **kwargs):
        if isinstance(e, first_argument_type):
            return f(e, *args, **kwargs)
        if hasattr(e, "attributes"):
            e.attributes = [inner(at, *args, **kwargs) for at in e.attributes]
    return inner

@dataclass
class Position():
    position: int
    world: World

@ability
def move(position: Position, displacement):
    position.position = (position.position + displacement) % len(position.world.landscape)
    return position

@ability
def move_plus_one(position: Position):
    position = move(position, 1)
    return position

@ability
def move_minus_one(position: Position):
    position = move(position, -1)
    return position

@ability
def random_walk(position: Position):
    position = random.choice([move_minus_one, move_plus_one])(position)
    return position


def render(gameworld: World) -> str:
    world = gameworld

    for entity in world.entities:
        world_before = world[:entity.position]
        world_after = world[entity.position+len(entity.representation):]
        world = world_before + entity.representation + world_after
    return world

def init_game():
    gameworld = World("_" * 10, [])
    robot_position = Position(0, gameworld)
    robot = Entity("robot", "R", attributes=[robot_position], abilities=[random_walk])
    gameworld.entities.extend([
        robot,
        Entity("cabinet", "C")
    ])
    def tick():
        random_walk(robot_position)
        sleep(0.2)
    return gameworld, tick


def main_curses(stdscr):
    gameworld, tick = init_game()
    stdscr.clear()
    while True:
        tick()
        stdscr.clear()
        stdscr.addstr(pformat(gameworld))
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main_curses)