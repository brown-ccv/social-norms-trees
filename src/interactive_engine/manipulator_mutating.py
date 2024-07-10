from dataclasses import dataclass, field
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

@dataclass
class MultiStore:
    contents: List[Any] = field(default_factory=list)


def take(thing: Any, from_: MultiStore, to_: MultiStore):
    """
        Examples:
            >>> s0 = MultiStore(["medicine"])
            >>> s1 = MultiStore()
            >>> s0, s1
            (MultiStore(contents=['medicine']), MultiStore(contents=[]))

            >>> take("medicine", s0, s1)
            >>> s0, s1
            (MultiStore(contents=[]), MultiStore(contents=['medicine']))
    """

    if thing not in from_.contents:
        raise EmptyError

    to_.contents.append(thing)
    from_.contents.remove(thing)
    return


class Manipulator(Entity):
    def __init__(self, thing: Optional[Entity]=None):
        self.thing = None

