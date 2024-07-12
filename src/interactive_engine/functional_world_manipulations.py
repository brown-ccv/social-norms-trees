from dataclasses import replace, dataclass, field
from itertools import accumulate
from typing import TypeVar, List, Union, Optional, Set, Iterable

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
class Location(Entity):
    entities: Set[EntityID] = field(default_factory=set)


def replace_in_list(list_, i, thing):
    new_list = list_[:i] + [thing] + list_[i + 1 :]
    return new_list


def move(entity_id: EntityID, location_id: EntityID, world: W) -> W:
    """Move an Entity in a world.

    Examples:
        >>> create(Location(), World())
        World(entities=[Location(id=0, entities=set())])

        >>> world = create(Entity(), create(Location(), World()))
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Entity(id=1, entities=[])])

        We can move an entity by its ID to a new location
        >>> move(1, 0, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={1}),
                        Entity(id=1, entities=[])])

        The function is idempotent
        >>> move(1, 0, move(1, 0, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={1}),
                        Entity(id=1, entities=[])])

        `world` is unchanged.
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Entity(id=1, entities=[])])


        >>> world = create(Entity(),
        ...         create(Entity(),
        ...         create(Location(),
        ...         create(Location(),
        ...                           World()))))
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Location(id=1, entities=set()),
                        Entity(id=2, entities=[]),
                        Entity(id=3, entities=[])])

        >>> move(3, 1, move(2, 0, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={2}),
                        Location(id=1, entities={3}),
                        Entity(id=2, entities=[]),
                        Entity(id=3, entities=[])])

        >>> move(2, 1, move(2, 0, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Location(id=1, entities={2}),
                        Entity(id=2, entities=[]),
                        Entity(id=3, entities=[])])


        >>> world = create(Entity(),
        ...         create(Location(),
        ...         create(Location(),
        ...         create(Location(),
        ...         create(Location(),
        ...                           World())))))
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Location(id=1, entities=set()),
                        Location(id=2, entities=set()),
                        Location(id=3, entities=set()),
                        Entity(id=4, entities=[])])
        >>> move(4, 0, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={4}),
                        Location(id=1, entities=set()),
                        Location(id=2, entities=set()),
                        Location(id=3, entities=set()),
                        Entity(id=4, entities=[])])

        >>> move(4, 1, move(4, 1, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Location(id=1, entities={4}),
                        Location(id=2, entities=set()),
                        Location(id=3, entities=set()),
                        Entity(id=4, entities=[])])

        >>> move(4, 2, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Location(id=1, entities=set()),
                        Location(id=2, entities={4}),
                        Location(id=3, entities=set()),
                        Entity(id=4, entities=[])])

        >>> move(4, 3, move(4, 2, move(4, 1, move(4, 0, world))))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities=set()),
                        Location(id=1, entities=set()),
                        Location(id=2, entities=set()),
                        Location(id=3, entities={4}),
                        Entity(id=4, entities=[])])

    """
    updated_entities = []

    # Remove the old entity_id from the old location (if there is one)
    old_locations = locate(entity_id, world)
    for old_location in old_locations:
        assert isinstance(old_location, Location)
        updated_old_location = replace(
            old_location, entities=old_location.entities - {entity_id}
        )
        updated_entities.append(updated_old_location)

    # Add the entity_id to the new Location
    location = world.entities[location_id]

    assert isinstance(location, Location)
    updated_new_location = replace(location, entities=location.entities | {entity_id})
    updated_entities.append(updated_new_location)

    new_world_entities = world.entities
    for updated_entity in updated_entities:
        new_world_entities = replace_in_list(
            new_world_entities, updated_entity.id, updated_entity
        )

    new_world = replace(world, entities=new_world_entities)
    return new_world


def locate(entity_id: EntityID, world: W) -> Iterable[Location]:
    """Locate an Entity in a world.

    Examples:
        >>> list(locate(1, create(Entity(), create(Location(), World()))))
        []

        >>> list(locate(1, move(1, 0, create(Entity(), create(Location(), World())))))
        [Location(id=0, entities={1})]
    """
    locations = filter(
        lambda e: isinstance(e, Location) and entity_id in e.entities, world.entities
    )
    return locations


if __name__ == "__main__":
    pass
