from dataclasses import dataclass, replace, field
from pprint import pprint
from typing import Callable, List, Optional, TypeVar

import click


@dataclass
class World:
    behavior: List["Behavior"] = field(default_factory=list)
    available_behaviors: List["Behavior"] = field(default_factory=list)


W = TypeVar("W", bound=World)

Behavior = Callable[[W], W]


def get_behavior_name(callback: Behavior) -> str:
    name = callback.__name__
    return name


def get_behavior_message(callback: Behavior) -> str:
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
        World(behavior=[], ...)

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
        index = click.prompt(text="Where would you like to insert it?", type=int)

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


@dataclass
class IntWorld(World):
    state: int = field(default=0)


def add_x(w: IntWorld, x: int = 1) -> IntWorld:
    new_world = replace(w, state=w.state + x)
    return new_world


def add_one(w: IntWorld) -> IntWorld:
    return add_x(w, 1)


def add_two(w: IntWorld) -> IntWorld:
    return add_x(w, 2)


def main(world):
    while True:
        for behavior in world.behavior:
            result = behavior(world)
            if result is not None and isinstance(result, type(world)):
                world = result
                print_world(world)


if __name__ == "__main__":
    world = IntWorld(
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
