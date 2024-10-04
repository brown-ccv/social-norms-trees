import copy
import py_trees
import json
import uuid
import importlib


def get_class(module, name):
    module_ = importlib.import_module(module)
    cls_ = getattr(module_, name)
    return cls_


def encode_py_trees_behavior(obj: py_trees.behaviour.Behaviour):
    dict_ = {
        "__module__": obj.__class__.__module__,
        "__name__": obj.__class__.__name__,
        "name": obj.name,
    }
    if isinstance(obj, py_trees.composites.Composite):
        dict_["children"] = [encode_py_trees_behavior(o) for o in obj.children]
        dict_["memory"] = obj.memory
    return dict_


def decode_py_trees_behavior(dict_):
    dict__ = copy.copy(dict_)
    dict__["children"] = [
        decode_py_trees_behavior(c) for c in dict_.get("children", [])
    ]
    cls = get_class(dict__.pop("__module__"), dict__.pop("__name__"))
    obj = cls(**dict__)
    return obj


def encode_uuid(obj: uuid.UUID) -> dict:
    dict_ = {
        "__module__": obj.__class__.__module__,
        "__name__": obj.__class__.__name__,
        "hex": obj.urn,
    }
    return dict_


def decode_uuid(dict_: dict) -> uuid.UUID:
    cls = get_class(dict_["__module__", "__name__"])
    obj = cls(dict_["hex"])
    return obj


class PyTreesEncoder(json.JSONEncoder):
    def default(self, obj):
        print(obj)
        if isinstance(obj, py_trees.behaviour.Behaviour):
            dict_ = encode_py_trees_behavior(obj)
            return dict_

        # Let the base class default method raise the TypeError
        return super().default(obj)


class PyTreesDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=PyTreesDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        if str(d.get("__module__")).startswith("py_trees."):
            cls = get_class(d.pop("__module__"), d.pop("__name__"))
            return cls(**d)
        return d


if __name__ == "__main__":
    tree = py_trees.composites.Sequence(
        "S0",
        False,
        children=[
            py_trees.behaviours.Dummy("A"),
        ],
    )
    print(py_trees.display.unicode_tree(tree))

    dumped = json.dumps(tree, cls=PyTreesEncoder)
    print(dumped)

    loaded = json.loads(dumped, cls=PyTreesDecoder)
    print(py_trees.display.unicode_tree(loaded))

    assert py_trees.display.unicode_tree(tree) == py_trees.display.unicode_tree(loaded)
