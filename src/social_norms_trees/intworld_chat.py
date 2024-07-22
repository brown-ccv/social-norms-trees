"""Example of using worlds with just an integer for the state of the world"""

from dataclasses import dataclass, field, replace

from social_norms_trees.chat import (
    World,
    print_world,
    update_behavior,
    add_behavior,
    remove_behavior,
    main,
)


@dataclass
class IntWorld(World):
    state: int = field(default=0)


def add_x(w: IntWorld, x: int = 1) -> IntWorld:
    """Add x to the state of the world"""
    new_world = replace(w, state=w.state + x)
    return new_world


def add_one(w: IntWorld) -> IntWorld:
    """Add 1 to the state of the world"""
    return add_x(w, 1)


def add_two(w: IntWorld) -> IntWorld:
    """Add 2 to the state of the world"""
    return add_x(w, 2)


if __name__ == "__main__":
    world_ = IntWorld(
        state=0,
        behavior=[print_world, add_one, update_behavior],
        available_behaviors=[
            print_world,
            update_behavior,
            add_behavior,
            remove_behavior,
            add_one,
            add_two,
        ],
    )
    main(world_)
