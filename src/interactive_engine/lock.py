from dataclasses import dataclass, field, replace
from functools import partial
from typing import Any

from interactive_engine.engine import Entity, ability


@dataclass
class Lock:
    """A lock.

    Examples:
        We can try to unlock it with the wrong secret – it doesn't work.
        >>> unlock(Lock(secret=4567, locked=True), secret=1234)
        Lock(secret=4567, locked=True)

        ... but if we use the right secret, it will unlock
        >>> unlock(Lock(secret=1234, locked=True), secret=1234)
        Lock(secret=1234, locked=False)
    """

    secret: Any = field(default="1234")
    locked: bool = field(default=False)


def make_key(secret="1234"):
    """
    Examples:
        >>> k = make_key(secret=1234)
        >>> l = Lock(secret=1234, locked=True)
        >>> k.abilities[0](l)
        Lock(secret=1234, locked=False)
    """
    key = Entity(abilities=[partial(unlock, secret=secret)])
    return key


@ability
def unlock(lock: Lock, secret="1234"):
    if secret == lock.secret:
        lock = replace(lock, locked=False)
    return lock
