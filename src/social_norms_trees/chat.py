"""Module for worlds which have mutable behaviors"""

from dataclasses import dataclass, replace, field
from pprint import pprint
from time import sleep
from typing import Callable, List, Optional, TypeVar, Literal

import click


@dataclass
class World:
    """Class which holds a list of active and available behaviors."""

    behavior: List["Behavior"] = field(default_factory=list)
    available_behaviors: List["Behavior"] = field(default_factory=list)


W = TypeVar("W", bound=World)

Behavior = Callable[[W], W]


def get_behavior_name(callback: Behavior) -> str:
    """Get the name of a callable Behavior"""
    name = callback.__name__
    return name


def get_behavior_message(callback: Behavior) -> str:
    """Get the top line of the docstring of a callable Behavior, or (if missing) its name"""
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


def list_behavior(world: World) -> str:
    """List all the behaviors and their indices"""
    behavior_listing = "\n".join(
        [f"{i}: {get_behavior_message(b)}" for i, b in enumerate(world.behavior)]
    )
    return behavior_listing


def add_behavior(
    world: World, behavior: Optional[Behavior] = None, index: Optional[int] = None
):
    """Add a behavior

    Examples:
        An empty world has no behaviors:
        >>> World()  # doctest: +ELLIPSIS
        World(behavior=[], ...)

        >>> def add_one(world):
        ...     # Dummy Behavior
        ...     return world

        We can add a behavior to the world:
        >>> add_behavior(World(), add_one, 0)  # doctest: +ELLIPSIS
        World(behavior=[<function add_one at 0x...>], ...)


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
        index = click.prompt(
            text=f"Where would you like to insert it?\n{list_behavior(world)}\n",
            type=int,
        )

    new_behavior = world.behavior[:index] + [behavior] + world.behavior[index:]
    new_world = replace(world, behavior=new_behavior)
    return new_world


def remove_behavior(world: World, index: Optional[int] = None):
    """Remove a behavior

    Examples:
        An empty world has no behaviors:
        >>> World()  # doctest: +ELLIPSIS
        World(behavior=[], ...)

        If we try to remove a behavior from an empty world, nothing happens:
        >>> remove_behavior(World(), index=0)  # doctest: +ELLIPSIS
        World(behavior=[], available_behaviors=[])

        >>> remove_behavior(World(), index=1)  # doctest: +ELLIPSIS
        World(behavior=[], available_behaviors=[])

        If we have a world with some behaviors:
        >>> def add_one(world):
        ...     return world
        >>> def add_two(world):
        ...     return world

        >>> World(behavior=[add_one, add_two])  # doctest: +ELLIPSIS
        World(behavior=[<function add_one at 0x...>, <function add_two at 0x...>], ...)

        ... we can remove one:
        >>> remove_behavior(World(behavior=[add_one, add_two]), index=1)  # doctest: +ELLIPSIS
        World(behavior=[<function add_one at 0x...>], ...)

        Trying to remove one beyond the limits of the list leaves the world unchanged:
        >>> remove_behavior(World(behavior=[add_one, add_two]), index=3)  # doctest: +ELLIPSIS
        World(behavior=[<function add_one at 0x...>, <function add_two at 0x...>], ...)

    """
    if index is None:
        text = f"Which behavior would you like to remove?\n{list_behavior(world)}\n"
        index = click.prompt(text=text, type=int)
    new_behavior = world.behavior[:index] + world.behavior[index + 1 :]
    new_world = replace(world, behavior=new_behavior)
    return new_world


def update_behavior(
    world: World,
    action: Optional[Literal["add", "remove", "skip"]] = None,
    behavior: Optional[Behavior] = None,
    index: Optional[int] = None,
) -> World:
    """Update a behavior"""
    if action is None:
        action = click.prompt(
            text="How would you like to update the behaviors?",
            default="skip",
            type=click.Choice(["add", "remove", "skip"]),
        )
    match action:
        case "add":
            new_world = add_behavior(world, behavior, index)
        case "remove":
            new_world = remove_behavior(world, index)
        case "skip" | _:
            new_world = world

    return new_world


def print_world(world: World):
    """Display the world"""

    pprint(world)
    return


def main(world):
    """Run the world's behaviors in a loop"""
    i = 0
    while True:
        behavior = world.behavior[i]
        result = behavior(world)
        if result is not None and isinstance(result, type(world)):
            world = result
            print_world(world)

        sleep(0.1)
        i += 1
        if i >= len(world.behavior):  # Loop back once we've done all the behaviors
            i = 0


if __name__ == "__main__":
    world_ = World(
        behavior=[print_world, update_behavior],
        available_behaviors=[
            print_world,
            update_behavior,
            add_behavior,
            remove_behavior,
        ],
    )
    main(world_)
