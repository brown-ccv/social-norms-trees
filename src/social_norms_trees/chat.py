import time
from dataclasses import dataclass, replace, field
import itertools
from collections import namedtuple
from functools import partial
from pprint import pprint
from typing import Callable, List, Iterable, Optional

import click


@dataclass
class World:
    state: int = field(default=0)
    behavior: List["Behavior"] = field(default_factory=list)
    available_behaviors: List["Behavior"] = field(default_factory=list)


@dataclass
class Behavior:
    name: str
    message: str
    callback: Callable[["World"], "World"]


def add_x(w: World, x: int = 1) -> World:
    new_world = replace(w, state=w.state + x)
    return new_world


def add_one(w: World) -> World:
    return add_x(w, 1)


def add_two(w: World) -> World:
    return add_x(w, 2)


def get_behavior_name(callback: Callable[["World"], "World"]) -> str:
    name = callback.__name__
    return name


def get_behavior_message(callback: Callable[["World"], "World"]) -> str:
    try:
        message = str.split(callback.__doc__, "\n")[0]
        assert message != ""
    except (
        IndexError,
        TypeError,
        AssertionError,
    ):  # docstring is empty or non-existent
        message = get_behavior_name(callback)

    return message


def add_behavior(
    world: World, behavior: Optional[Behavior] = None, index: Optional[int] = None
):
    """Add a behavior

    Examples:
        An empty world has no behaviors:
        >>> World()  # doctest: +ELLIPSIS
        World(..., behavior=[], ...)

        We can add a behavior to the world:
        >>> add_behavior(World(), add_one, 0)  # doctest: +ELLIPSIS
        World(..., behavior=[<function add_one at 0x...>], ...)
    """

    if behavior is None:
        behavior_text = click.prompt(
            text="Which behavior would you like to add?",
            type=click.Choice(
                [get_behavior_message(b) for b in world.available_behaviors]
            ),
        )
        behavior = next(
            b
            for b in world.available_behaviors
            if get_behavior_message(b) == behavior_text
        )
    if index is None:
        index = click.prompt(text="Where would you like to insert it?", type=int)

    new_behavior = world.behavior[:index] + [behavior] + world.behavior[index:]
    new_world = replace(world, behavior=new_behavior)
    return new_world


def remove_behavior(world: World, index: Optional[int] = None):
    """Remove a behavior"""
    if index is None:
        behavior_listing = "\n".join(
            [f"{i}: {get_behavior_message(b)}" for i, b in enumerate(world.behavior)]
        )
        text = "Which behavior would you like to remove?\n" + behavior_listing + "\n"
        index = click.prompt(text=text, type=int)
    new_behavior = world.behavior[:index] + world.behavior[index + 1 :]
    new_world = replace(world, behavior=new_behavior)
    return new_world


def print_world(world: World):
    """"""

    pprint(world)
    return


def main(world):
    while True:
        for behavior in world.behavior:
            result = behavior(world)
            if result is not None and isinstance(result, type(world)):
                world = result
                print_world(world)


if __name__ == "__main__":
    world = World(
        state=0,
        behavior=[print_world, remove_behavior, add_one, add_behavior],
        available_behaviors=[
            print_world,
            add_behavior,
            remove_behavior,
            add_one,
            add_two,
        ],
    )
    main(world)
