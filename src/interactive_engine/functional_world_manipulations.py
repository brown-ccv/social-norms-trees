from dataclasses import replace, dataclass, field
from typing import TypeVar, List, Union, Optional, Set, Iterable, Type, Sequence

from interactive_engine.world import World


EntityID = int


@dataclass
class Entity:
    """A thing in a world"""

    id: Optional[EntityID] = field(compare=False, default=None)


@dataclass
class World:
    """A container for a whole world of entities"""

    entities: List[Union[Entity, EntityID]] = field(default_factory=list)


W = TypeVar("W", bound=World)


def create(entity: Entity, world: W) -> W:
    """Create a new Entity in a world.
    Examples:
        >>> world = World()
        >>> world
        World(entities=[])

        >>> create(Entity(), world)
        World(entities=[Entity(id=0)])

        >>> create(Entity(), create(Entity(), world))
        ... # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Entity(id=0), Entity(id=1)])
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
        World(entities=[Entity(id=0), Entity(id=1)])

        >>> destroy(0, world)
        World(entities=[None, Entity(id=1)])

        >>> destroy(world.entities[1], world)
        World(entities=[Entity(id=0), None])

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
            matching_entities = identify_all(entity, world)
            new_world = world
            for matching_entity in matching_entities:
                new_world = destroy(matching_entity, new_world)
            return new_world

        case Entity(id=id_):
            # we're given an Entity with an ID, so we can just destroy based on the EntityID
            return destroy(id_, world)
        case EntityID() as id_:
            # we're given an Entity ID, so we can slice it out of the list
            new_world = replace(
                world,
                entities=world.entities[:id_] + [None] + world.entities[id_ + 1 :],
            )
            return new_world


def identify(entity: Union[Entity, EntityID], world: W) -> Optional[Entity]:
    """Given an id or an entity (which may not have an ID), find matching entities.
    Examples:
        We can pass in an entity without an ID and get the fully resolved entity back.
        >>> identify(Entity(), create(Entity(), World()))
        Entity(id=0)

        We can pass in an entity ID and get the entity back.
        >>> identify(0, create(Entity(), World()))
        Entity(id=0)

        If there's no matching entity, then it returns None.
        >>> identify(Entity(id=1), create(Entity(), World()))
        Traceback (most recent call last):
        ...
        LookupError: Entity Entity(id=1) not found.
    """
    match entity:
        case EntityID():
            resolved_entity = world.entities[entity]
        case Entity(id=None):
            matching_entities = filter(lambda e: e == entity, world.entities)
            resolved_entity = next(matching_entities, None)
        case Entity(id=id_):
            matching_entities = filter(
                lambda e: e == entity and e.id == id_, world.entities
            )
            resolved_entity = next(matching_entities, None)
        case _:
            resolved_entity = None
    if resolved_entity is None:
        raise LookupError(f"Entity {entity} not found.")
    return resolved_entity


def identify_all(entity: Union[Entity, EntityID], world: W) -> Sequence[Entity]:
    """Given an id or an entity (which may not have an ID), find matching entities.
    Examples:
        We can pass in an entity without an ID and get the fully resolved entity back.
        >>> list(identify_all(Entity(), create(Entity(), World())))
        [Entity(id=0)]

        We can pass in an entity ID and get the entity back.
        >>> list(identify_all(0, create(Entity(), World())))
        [Entity(id=0)]

        If there's no matching entity, then it returns None.
        >>> list(identify_all(Entity(id=1), create(Entity(), World())))
        []
    """
    match entity:
        case EntityID():
            matching_entities = [world.entities[entity]]
        case Entity(id=None):
            matching_entities = filter(lambda e: e == entity, world.entities)
        case Entity(id=id_):
            matching_entities = filter(
                lambda e: e == entity and e.id == id_, world.entities
            )
        case _:
            matching_entities = []
    return matching_entities


@dataclass
class Tracker(Entity):
    """An entity which tracks links with other entities."""

    entities: Set[EntityID] = field(default_factory=set, compare=False)


@dataclass
class Location(Tracker):
    """A place in the world where entities can be."""

    name: str = ""


@dataclass
class Agent(Entity):
    """An Entity with a name and some behavior."""

    name: str = ""


def replace_in_list(list_, i, thing):
    new_list = list_[:i] + [thing] + list_[i + 1 :]
    return new_list


def update_entity_list(entity: Entity, entities: List[Entity]):
    new_entity_list = replace_in_list(entities, entity.id, entity)
    return new_entity_list


def move(
    entity_id: Union[Entity, EntityID], location_id: Union[Tracker, EntityID], world: W
) -> W:
    """Move an Entity in a world.

    Examples:
        >>> create(Tracker(), World())
        World(entities=[Tracker(id=0, entities=set())])

        >>> world = create(Entity(), create(Tracker(), World()))
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Entity(id=1)])

        We can move an entity by its ID to a new location
        >>> move(1, 0, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities={1}),
                        Entity(id=1)])

        The function is idempotent
        >>> move(1, 0, move(1, 0, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities={1}),
                        Entity(id=1)])

        `world` is unchanged.
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Entity(id=1)])


        We can move an entity by its definition (incomplete):
        >>> move(Entity(), 0, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities={1}),
                        Entity(id=1)])

        Or its complete definition:
        >>> move(Entity(id=1), 0, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities={1}),
                        Entity(id=1)])

        ... but an inconsistent definition will cause an error:
        >>> move(Entity(id=10), 0, world)  # doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
        ...
        LookupError: Entity Entity(id=10) not found.

        >>> world = create(Entity(),
        ...         create(Entity(),
        ...         create(Tracker(),
        ...         create(Tracker(),
        ...                           World()))))
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Tracker(id=1, entities=set()),
                        Entity(id=2),
                        Entity(id=3)])

        >>> move(3, 1, move(2, 0, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities={2}),
                        Tracker(id=1, entities={3}),
                        Entity(id=2),
                        Entity(id=3)])

        >>> move(2, 1, move(2, 0, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Tracker(id=1, entities={2}),
                        Entity(id=2),
                        Entity(id=3)])


        If we have a series of trackers, the entity can move through them, existing only in one
        at each time:
        >>> world = create(Entity(),
        ...         create(Tracker(),
        ...         create(Tracker(),
        ...         create(Tracker(),
        ...         create(Tracker(),
        ...                           World())))))
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Tracker(id=1, entities=set()),
                        Tracker(id=2, entities=set()),
                        Tracker(id=3, entities=set()),
                        Entity(id=4)])
        >>> move(4, 0, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities={4}),
                        Tracker(id=1, entities=set()),
                        Tracker(id=2, entities=set()),
                        Tracker(id=3, entities=set()),
                        Entity(id=4)])

        >>> move(4, 1, move(4, 1, world))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Tracker(id=1, entities={4}),
                        Tracker(id=2, entities=set()),
                        Tracker(id=3, entities=set()),
                        Entity(id=4)])

        >>> move(4, 2, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Tracker(id=1, entities=set()),
                        Tracker(id=2, entities={4}),
                        Tracker(id=3, entities=set()),
                        Entity(id=4)])

        >>> move(4, 3, move(4, 2, move(4, 1, move(4, 0, world))))  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Tracker(id=0, entities=set()),
                        Tracker(id=1, entities=set()),
                        Tracker(id=2, entities=set()),
                        Tracker(id=3, entities={4}),
                        Entity(id=4)])

        If there are multiple kinds of trackers, we can specify a single type to be affected:
        >>> @dataclass
        ... class Faction(Tracker):
        ...     name: str = ""
        >>> world = World()
        >>> entities = [Location(name="north"),
        ...             Location(name="south"),
        ...             Faction(name="blue"),
        ...             Faction(name="green"),
        ...             Entity()]
        >>> for e in entities:
        ...     world = create(e, world)


        In this world, the entity 4 is in faction 2, and location 0:
        >>> world = move(4, 2, world)  # doctest: +NORMALIZE_WHITESPACE
        >>> world = move(4, 0, world)
        >>> world  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={4}, name='north'),
                        Location(id=1, entities=set(), name='south'),
                        Faction(id=2, entities={4}, name='blue'),
                        Faction(id=3, entities=set(), name='green'),
                        Entity(id=4)])

        Now when we move faction (from 2) to 3, the location isn't changed:
        >>> move(4, 3, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={4}, name='north'),
                        Location(id=1, entities=set(), name='south'),
                        Faction(id=2, entities=set(), name='blue'),
                        Faction(id=3, entities={4}, name='green'),
                        Entity(id=4)])

        We can also move objects to an entity which is incompletely defined:
        >>> move(4, Faction(name="blue"), world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={4}, name='north'),
                        Location(id=1, entities=set(), name='south'),
                        Faction(id=2, entities={4}, name='blue'),
                        Faction(id=3, entities=set(), name='green'),
                        Entity(id=4)])

        ... or completely defined:
        >>> move(4, Faction(id=2, name="blue"), world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={4}, name='north'),
                        Location(id=1, entities=set(), name='south'),
                        Faction(id=2, entities={4}, name='blue'),
                        Faction(id=3, entities=set(), name='green'),
                        Entity(id=4)])

        But an inconsistent entity will cause an error:
        >>> move(4, Faction(id=10, name="blue"), world)  # doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
        ...
        LookupError: Entity Faction(id=10, entities=set(), name='blue') not found.

        We can also move objects by their (incomplete) definition:
        >>> move(Entity(), 2, world)  # doctest: +NORMALIZE_WHITESPACE
        World(entities=[Location(id=0, entities={4}, name='north'),
                        Location(id=1, entities=set(), name='south'),
                        Faction(id=2, entities={4}, name='blue'),
                        Faction(id=3, entities=set(), name='green'),
                        Entity(id=4)])


    """
    # Get the new location so we can see what kinds of trackers we need to modify
    location = identify(location_id, world)
    entity = identify(entity_id, world)
    kind = type(location)

    updated_entities = []

    # Remove the old entity_id from the old location (if there is one)
    old_locations = locate(entity.id, world, kind=kind)
    for old_location in old_locations:
        assert isinstance(old_location, kind)
        updated_old_location = replace(
            old_location, entities=old_location.entities - {entity.id}
        )
        updated_entities.append(updated_old_location)

    # Add the entity_id to the new Tracker
    assert isinstance(location, kind)

    updated_new_location = replace(location, entities=location.entities | {entity.id})
    updated_entities.append(updated_new_location)

    new_world_entities = world.entities
    for updated_entity in updated_entities:
        new_world_entities = update_entity_list(updated_entity, new_world_entities)

    new_world = replace(world, entities=new_world_entities)
    return new_world


T = TypeVar("T", bound=Tracker)


def locate(
    entity_id: Union[Entity, EntityID], world: W, kind: Type[T] = Tracker
) -> Iterable[T]:
    """Locate an Entity in a world.

    Examples:
        >>> list(locate(1, create(Entity(), create(Tracker(), World()))))
        []

        >>> list(locate(1, move(1, 0, create(Entity(), create(Tracker(), World())))))
        [Tracker(id=0, entities={1})]

        >>>
    """
    if isinstance(entity_id, Entity):
        resolved_entity = identify(entity_id, world)
        return locate(resolved_entity.id, world, kind=kind)
    else:
        locations = filter(
            lambda e: isinstance(e, kind) and entity_id in e.entities,
            world.entities,
        )
        return locations


if __name__ == "__main__":
    from pprint import pprint
    import random
    import time

    world = World()
    for entity in [
        Location(name="Library"),
        Location(name="Dining Room"),
        Location(name="Kitchen"),
        Location(name="Hallway"),
        Location(name="Lounge"),
        Location(name="Ballroom"),
        Location(name="Conservatory"),
        Location(name="Billiard Room"),
        Location(name="Study"),
        Agent(name="Miss Scarlet"),
        Agent(name="Professor Plum"),
    ]:
        world = create(entity, world)
    pprint(world)

    locations = list(filter(lambda e: isinstance(e, Location), world.entities))
    scarlet, plum = list(filter(lambda e: isinstance(e, Agent), world.entities))
    plum_next_location = 0

    while True:

        world = move(scarlet, random.choice(locations).id, world)

        # plum trying to stay 1 ahead of scarlet
        world = move(plum, plum_next_location, world)

        pprint(world)

        print(next(iter(locate(plum, world))), next(iter(locate(scarlet, world))))

        if list(locate(plum, world)) == list(locate(scarlet, world)):
            print("Game over!")
            break

        scarlet_last_location = next(iter(locate(scarlet.id, world)))
        plum_next_location = (scarlet_last_location.id + 1) % len(locations)

        time.sleep(1)
