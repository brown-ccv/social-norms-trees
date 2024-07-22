import time
from dataclasses import dataclass, replace
import itertools
from collections import namedtuple
from functools import partial
from pprint import pprint
from typing import Callable, List, Iterable, Optional

import click


@dataclass
class World:
    state: int
    behavior: List["Behavior"]
    available_behaviors: List["Behavior"]


@dataclass
class Behavior:
    name: str
    message: str
    callback: Callable[["World"], "World"]


all_behaviors = [
    Behavior(
        "add_one",
        "Add one to the state",
        add_one := lambda w: replace(w, state=w.state + 1),
    ),
    Behavior(
        "add_two",
        "Add two to the state",
        add_two := lambda w: replace(w, state=w.state + 2),
    ),
]


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


def register_behavior(
    callback: Callable[["World"], "World"], behavior_list=all_behaviors
):
    """Register a behavior to the list of all behaviors

    Introspects to get the message to be included with the behavior from the top line of the
    docstring.
    """
    name = get_behavior_name(callback)
    message = get_behavior_message(callback)
    behavior_list.append(Behavior(name, message, callback))
    return callback


@register_behavior
def add_behavior(
    world: World, behavior: Optional[Behavior] = None, index: Optional[int] = None
):
    """Add a behavior"""

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

    new_behavior = world.behavior[:index] + [behavior.callback] + world.behavior[index:]
    new_world = replace(world, behavior=new_behavior)
    return new_world


@register_behavior
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


@register_behavior
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
