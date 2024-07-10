import curses
from functools import partial
from pprint import pformat

from interactive_engine.text_world import (
    render,
    init_game,
)


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
    curses.wrapper(main_curses)
