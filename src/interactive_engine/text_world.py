import random
from dataclasses import dataclass
from time import sleep
from typing import List, Optional

from interactive_engine.engine import Entity, get_attributes, ability
from interactive_engine.world import World


@dataclass
class TextWorld(World):
    landscape: str

@dataclass
class TextAppearance:
    representation: Optional[str]


def render(gameworld: TextWorld) -> str:
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


@dataclass
class Position:
    position: int
    world: TextWorld


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


def init_game():
    gameworld = TextWorld("_" * 15, [])
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
