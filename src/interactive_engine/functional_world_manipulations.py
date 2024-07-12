from dataclasses import replace, dataclass, field
from typing import TypeVar, List

from interactive_engine.engine import Entity
from interactive_engine.world import World

W = TypeVar("W", bound=World)


def create(entity: Entity, world: W) -> W:
    """Create a new Entity in a world.
    Examples:
        >>> world = World()
        >>> world
        World(entities=[])

        >>> create(Entity(), world)
        World(entities=[Entity(name=None, attributes=[], abilities=[])])

        >>> create(Entity(), create(Entity(), world))
        ... # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Entity(name=None, attributes=[], abilities=[]),
                        Entity(name=None, attributes=[], abilities=[])])
    """
    world = replace(world, entities=world.entities + [entity])
    return world


def destroy(entity: Entity, world: W) -> W:
    """Destroy an Entity in a world.

    Examples:
        >>> destroy(Entity(), World())
        World(entities=[])

        >>> destroy(Entity(), create(Entity(), World()))
        World(entities=[])

        >>> destroy(Entity(), create(Entity(), create(Entity(), World())))
        ... # doctest: +NORMALIZE_WHITESPACE
        World(entities=[])
    """
    world = replace(world, entities=list(filter(lambda e: e != entity, world.entities)))
    return world


@dataclass
class Location:
    name: str
    entities: List[Entity] = field(default_factory=list)


def locate(entity: Entity, world: W) -> List[Location]:
    """Locate an Entity in a world.

    Examples:
        >>> locate(Entity(), World())
        []
        >>> w = World()

        >>> locate(Entity(attributes=[Location("")]), World())
    """
    location = list(
        filter(
            lambda a: isinstance(a, Location) and a.world == world, entity.attributes
        )
    )
    return location


def move_to(entity: Entity, world: W, location: Location) -> W:
    """Move an Entity in a world.

    Examples:
        >>> e = Entity()
        >>> world = World(entities=[e])
        >>> world
        World(entities=[Entity(name=None, attributes=[], abilities=[])])

        >>> l = Location("here", world)
        >>> move_to(e, world, l)
        World(entities=[Entity(name=None, attributes=[Location(name='here', world=World(entities=[Entity(name=None, attributes=[], abilities=[])]))], abilities=[])])

    """
    filtered_attributes = filter(
        lambda a: not (isinstance(a, Location)), entity.attributes
    )
    new_entity = replace(entity, attributes=[location] + list(filtered_attributes))
    new_entities = [new_entity] + list(filter(lambda e: e != entity, world.entities))
    new_world = replace(world, entities=new_entities)
    return new_world


def move_to_unrecursive(
    entity: Entity,
    location: Location,
    world: W,
) -> W:
    """Move an Entity in a world.

    Examples:
        >>> l = Location("here")
        >>> world = create(l, World())
        >>> world
        World(entities=[Location(name='here', entities=[])])

        >>> e = Entity()
        >>> create(e, world)  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        World(entities=[Location(name='here', entities=[]), Entity(...)])

        >>> move_to_unrecursive(e, l, create(e, world)) # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        World(entities=[Location(name='here', entities=[Entity(...)])])

    """
    new_location = replace(location, entities=location.entities + [entity])

    filtered_attributes = filter(
        lambda a: not (isinstance(a, Location)), entity.attributes
    )

    new_entity = replace(entity, attributes=[location] + list(filtered_attributes))
    new_entities = [new_entity] + list(filter(lambda e: e != entity, world.entities))
    new_world = replace(world, entities=new_entities)
    return new_world


if __name__ == "__main__":
    world = World()
    print(world)
    print(create(entity=Entity(), world=world))
    print(destroy(Entity(), create(Entity(), world)))
