import curses
import inspect
import random
from dataclasses import dataclass, field
from functools import partial, wraps
from pprint import pprint, pformat
from time import sleep
from typing import Sequence, List, Any, Optional, Union, TypeVar, Type


@dataclass
class World:
    landscape: str
    entities: List["Entity"]


@dataclass
class Entity:
    name: str
    attributes: List[Union["Entity", dataclass]] = field(default_factory=list)
    abilities: List[Any] = field(default_factory=list)


def ability(f):
    """Decorator for abilities."""
    first_argument_type = next(
        iter(inspect.signature(f).parameters.values())
    ).annotation

    @wraps(f)
    def inner(e, *args, **kwargs):
        if isinstance(e, first_argument_type):
            e = f(e, *args, **kwargs)
        if hasattr(e, "attributes"):
            e.attributes = [inner(at, *args, **kwargs) for at in e.attributes]
        if hasattr(e, "entities"):
            e.entities = [inner(e, *args, **kwargs) for e in e.entities]
        return e

    return inner


@dataclass
class Position:
    position: int
    world: World


@ability
def move(position: Position, displacement):
    position.position = (position.position + displacement) % len(
        position.world.landscape
    )
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


T = TypeVar("T")


def get_attributes(entity: Entity, kind: Type[T]) -> Sequence[T]:
    return filter(lambda a: isinstance(a, kind), entity.attributes)


@dataclass
class TextAppearance:
    representation: Optional[str]


def render(gameworld: World) -> str:
    landscape = gameworld.landscape
    for entity in gameworld.entities:
        try:
            appearance = next(iter(get_attributes(entity, TextAppearance)))
        except StopIteration:
            continue
        for p in get_attributes(entity, Position):
            world_before = landscape[: p.position]
            world_after = landscape[p.position + len(appearance.representation) :]
            landscape = world_before + appearance.representation + world_after
    return landscape


def init_game():
    gameworld = World("_" * 15, [])
    robot = Entity(
        name="robot",
        attributes=[
            Position(0, gameworld),
            Position(2, gameworld),
            TextAppearance("R"),
        ],
        abilities=[random_walk],
    )
    gameworld.entities.extend(
        [
            robot,
            Entity(
                name="cabinet", attributes=[Position(5, gameworld), TextAppearance("C")]
            ),
        ]
    )

    def tick():
        random_walk(robot)
        sleep(0.15)

    return gameworld, tick


def main_curses(stdscr, render=render):
    world, tick = init_game()
    stdscr.clear()
    while True:

        stdscr.clear()
        stdscr.addstr(render(world))
        stdscr.refresh()
        tick()


main_debug = partial(
    main_curses, render=lambda world: f"{render(world)}\n{pformat(world)}"
)

if __name__ == "__main__":
    curses.wrapper(main_debug)
