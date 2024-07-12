from dataclasses import replace, dataclass, field
from typing import TypeVar, List, Union, Optional, Set, Iterable

from interactive_engine.world import World

W = TypeVar("W", bound=World)

EntityID = int


@dataclass
class Entity:
    id: Optional[EntityID] = field(compare=False, default=None)


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
class Tracker(Entity):
    entities: Set[EntityID] = field(default_factory=set, compare=False)


def replace_in_list(list_, i, thing):
    new_list = list_[:i] + [thing] + list_[i + 1 :]
    return new_list


def update_entity_list(entity: Entity, entities: List[Entity]):
    new_entity_list = replace_in_list(entities, entity.id, entity)
    return new_entity_list


def move(entity_id: EntityID, location_id: EntityID, world: W) -> W:
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

    """
    assert isinstance(entity_id, EntityID)
    assert isinstance(location_id, EntityID)

    updated_entities = []

    # Remove the old entity_id from the old location (if there is one)
    old_locations = locate(entity_id, world)
    for old_location in old_locations:
        assert isinstance(old_location, Tracker)
        updated_old_location = replace(
            old_location, entities=old_location.entities - {entity_id}
        )
        updated_entities.append(updated_old_location)

    # Add the entity_id to the new Tracker
    location = world.entities[location_id]

    assert isinstance(location, Tracker)
    updated_new_location = replace(location, entities=location.entities | {entity_id})
    updated_entities.append(updated_new_location)

    new_world_entities = world.entities
    for updated_entity in updated_entities:
        new_world_entities = update_entity_list(updated_entity, new_world_entities)

    new_world = replace(world, entities=new_world_entities)
    return new_world


def locate(entity_id: EntityID, world: W) -> Iterable[Tracker]:
    """Locate an Entity in a world.

    Examples:
        >>> list(locate(1, create(Entity(), create(Tracker(), World()))))
        []

        >>> list(locate(1, move(1, 0, create(Entity(), create(Tracker(), World())))))
        [Tracker(id=0, entities={1})]
    """
    locations = filter(
        lambda e: isinstance(e, Tracker) and entity_id in e.entities, world.entities
    )
    return locations


if __name__ == "__main__":
    from pprint import pprint
    import random
    import time

    @dataclass
    class Location(Tracker):
        name: str = ""

    @dataclass
    class Agent(Entity):
        name: str = ""

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

        world = move(scarlet.id, random.choice(locations).id, world)

        # plum trying to stay 1 ahead of scarlet
        world = move(plum.id, plum_next_location, world)

        pprint(world)

        print(list(locate(plum.id, world)), list(locate(scarlet.id, world)))

        if list(locate(plum.id, world)) == list(locate(scarlet.id, world)):
            print("Game over!")
            break

        scarlet_last_location = next(iter(locate(scarlet.id, world)))
        plum_next_location = (scarlet_last_location.id + 1) % len(locations)

        time.sleep(1)
