import inspect
from dataclasses import dataclass, field
from functools import wraps
from typing import Sequence, List, Any, Union, TypeVar, Type


@dataclass
class Entity:
    name: str = None
    attributes: List[Union["Entity", dataclass]] = field(default_factory=list)
    abilities: List[Any] = field(default_factory=list)


def ability(f):
    """Decorator for abilities."""
    first_argument_type = next(
        iter(inspect.signature(f).parameters.values())
    ).annotation

    @wraps(f)
    def inner(e, *args, **kwargs):
        if isinstance(e, first_argument_type):
            e = f(e, *args, **kwargs)
        if hasattr(e, "attributes"):
            e.attributes = [inner(at, *args, **kwargs) for at in e.attributes]
        if hasattr(e, "entities"):
            e.entities = [inner(e, *args, **kwargs) for e in e.entities]
        return e

    return inner


T = TypeVar("T")


def get_attributes(entity: Entity, kind: Type[T]) -> Sequence[T]:
    return filter(lambda a: isinstance(a, kind), entity.attributes)
