from dataclasses import field
from typing import Any

from interactive_engine.engine import Entity, ability


class Container(Entity):
    contents: list = field(default_factory=list)

    def take(self, thing: Any, allow=lambda: True):
        if allow():
            self.contents.remove(thing)
            return thing
        else:
            return

    def put(self, thing: Any, allow=lambda: True):
        if allow():
            self.contents.append(thing)
        return

@ability
def take(thing: Any, container: Container):
    try:
        container.take(thing)
        return thing, container
    except:
        return None, container


@ability
def put(thing: Any, container: Container):
    try:
        container.put(thing)
    except:
        pass
    return container

