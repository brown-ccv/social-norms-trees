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


def get_abilities(entity: Entity):
    """
    Examples:
        >>> list(get_abilities(Entity()))
        []
        >>> @ability
        ... def an_ability(target: Entity):
        ...     return
        >>> list(get_abilities(Entity(abilities=[an_ability])))  # doctest: +ELLIPSIS
        [<function an_ability at 0x...>]

        >>> @dataclass
        ... class Container(Entity):
        ...     contents: list = field(default_factory=list)
        >>> def make_bag_of_holding():
        ...     _container = Container()
        ...     def insert(entity: Entity):
        ...         return replace(_container, contents=_container.contents + [entity])
        ...     def remove(entity: Entity):
        ...         new_contents = _container.contents.copy().remove(entity)
        ...         return replace(_container, contents=new_contents)
        ...     bag_of_holding = Entity(attributes=[_container],
        ...         abilities=[insert, remove])
        ...     return bag_of_holding
        >>> list(get_abilities(Entity(attributes=[make_bag_of_holding()])))
        ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [<function make_bag_of_holding.<locals>.insert at 0x...>,
         <function make_bag_of_holding.<locals>.remove at 0x...>]

         >>> list(get_abilities(Entity(abilities=[an_ability], attributes=[make_bag_of_holding()])))
         ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
         [<function an_ability at 0x...>,
          <function make_bag_of_holding.<locals>.insert at 0x...>,
          <function make_bag_of_holding.<locals>.remove at 0x...>]

    """
    if hasattr(entity, "abilities"):
        for _ability in entity.abilities:
            yield _ability
    if hasattr(entity, "attributes"):
        for attribute in entity.attributes:
            for _ability in get_abilities(attribute):
                yield _ability
