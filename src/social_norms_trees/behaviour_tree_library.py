from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Behaviour:
    name: str
    id: Optional[str] = None
    parent: Optional[str] = None

@dataclass
class Sequence:
    name: str
    memory: bool
    children: List[Behaviour] = field(default_factory=list)  # Ensure a new list for each instance

    def add_child(self, child: Behaviour):
        child.parent = self
        self.children.append(child)

    def insert_child(self, child: Behaviour, index: int):
        if 0 <= index <= len(self.children):
            child.parent = self
            self.children.insert(index, child)

    def remove_child(self, child: Behaviour):
        if child in self.children:
            child.parent = None
            self.children.remove(child)