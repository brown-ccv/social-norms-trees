from dataclasses import dataclass, field, replace
from typing import Optional, Any, List

from interactive_engine.engine import Entity, ability


@dataclass
class Store:
    thing: Optional[Any] = field(default=None)


class FullError(Exception):
    pass

class EmptyError(Exception):
    pass


def move(from_: Store, to_: Store):
    """
    Examples:
        >>> s0 = Store("medicine")
        >>> s1 = Store()
        >>> s0, s1
        (Store(thing='medicine'), Store(thing=None))

        >>> move(s0, s1)
        >>> s0, s1
        (Store(thing=None), Store(thing='medicine'))
    """

    if to_.thing is not None:
        raise FullError
    if from_.thing is None:
        raise EmptyError

    to_.thing = from_.thing
    from_.thing = None
    return

@dataclass(frozen=True)
class MultiStore:
    contents: List[Any] = field(default_factory=list)


def take(from_: Store):
    """
        Examples:
            >>> s0 = Store("medicine")
            >>> take(s0)
            ('medicine', Store(thing=None))

            The original s0 isn't modified
            >>> s0
            Store(thing='medicine')

    """
    if from_.thing is None:
        raise EmptyError

    thing = from_.thing
    from_ = replace(from_, thing=None)
    return thing, from_

def give(thing, to_: Store):
    """
    Examples:
        >>>
    """


class Manipulator(Entity):
    def __init__(self, thing: Optional[Entity]=None):
        self.thing = None

