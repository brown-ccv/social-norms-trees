from dataclasses import replace, dataclass, field
from itertools import accumulate
from typing import TypeVar, List, Union, Optional

from interactive_engine.world import World

W = TypeVar("W", bound=World)

EntityID = int


@dataclass
class Entity:
    id: Optional[EntityID] = field(compare=False, default=None)
    entities: List[Union["Entity", EntityID]] = field(default_factory=list)


@dataclass
class World:
    entities: List[Union["Entity", EntityID]] = field(default_factory=list)


def create(entity: Entity, world: W) -> W:
    """Create a new Entity in a world.
    Examples:
        >>> world = World()
        >>> world
        World(entities=[])

        >>> create(Entity(), world)
        World(entities=[Entity(id=0, entities=[])])

        >>> create(Entity(), create(Entity(), world))
        ... # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Entity(id=0, entities=[]), Entity(id=1, entities=[])])
    """
    next_id = EntityID(len(world.entities))
    new_entity = replace(entity, id=next_id)
    new_world = replace(world, entities=world.entities + [new_entity])
    return new_world


def destroy(entity: Union[Entity, EntityID], world: W) -> W:
    """Destroy an Entity in a world.

    Examples:
        >>> world = create(Entity(), create(Entity(), World()))
        >>> world
        World(entities=[Entity(id=0, entities=[]), Entity(id=1, entities=[])])

        >>> destroy(0, world)
        World(entities=[None, Entity(id=1, entities=[])])

        >>> destroy(world.entities[1], world)
        World(entities=[Entity(id=0, entities=[]), None])

        >>> destroy(Entity(), World())
        World(entities=[])

        >>> destroy(Entity(), create(Entity(), World()))
        World(entities=[None])

        >>> destroy(Entity(), create(Entity(), create(Entity(), World())))
        ... # doctest: +NORMALIZE_WHITESPACE
        World(entities=[None, None])
    """
    match entity:
        case Entity(id=None):
            # try to locate the entity without the ID and destroy it
            matching_entities = filter(lambda e: e == entity, world.entities)
            new_world = world
            for matching_entity in matching_entities:
                new_world = destroy(matching_entity, new_world)
            return new_world

        case Entity(id=id_):
            # we're given an Entity with an ID, so we can just destroy based on the EntityID
            return destroy(id_, world)
        case id_:
            # we're given an Entity ID, so we can slice it out of the list
            new_world = replace(
                world,
                entities=world.entities[:id_] + [None] + world.entities[id_ + 1 :],
            )
            return new_world


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
