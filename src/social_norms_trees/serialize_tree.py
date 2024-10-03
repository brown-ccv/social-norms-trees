import py_trees
from social_norms_trees.custom_node_library import CustomBehavior, CustomSequence


def serialize_tree(tree):
    def serialize_node(node):
        data = {
            "type": node.__class__.__name__,
            "name": node.name,
            "children": [serialize_node(child) for child in node.children],
        }
        return data

    return serialize_node(tree)

def deserialize_tree(tree, behavior_library):
    def deserialize_node(node):
        assert type(node['type'] == str), (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Invalid type for node attribute 'type' found for node '{node['name']}'. "
            f"Please ensure that the 'name' attribute is a string."
        )
        assert type(node['name'] == str), (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Invalid type for node attribute 'name' found for node '{node['name']}'. "
            f"Please ensure that the 'name' attribute is a string."
        )

        node_type = node['type']
        assert node_type in ["Sequence", "Selector", "Behavior"], (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Invalid node type '{node_type}' found for node '{node['name']}'. "
            f"Please ensure that all node types are correct and supported."
        )

        behavior = behavior_library.get_behavior_by_display_name(node['name'])

        if node_type == 'Sequence':

            children = [deserialize_node(child) for child in node['children']]
            
            if behavior:
                return CustomSequence(
                    name=behavior['display_name'],
                    id_=behavior['id'],
                    display_name=behavior['display_name'],
                    children=children
                )
            else:
                raise ValueError(f"Behavior {node['name']} not found in behavior library")
        
        #TODO: node type Selector 
            
        elif node_type == 'Behavior':
            
            assert ('children' not in node or len(node['children']) == 0), (
            f"\nThere was an invalid configuration detected in the inputted behavior tree: "
            f"Children were detected for Behavior type node '{node['name']}': "
            f"Behavior nodes should not have any children. Please check the structure of your behavior tree."
    )

            if behavior:
                return CustomBehavior(
                    name=behavior['display_name'],
                    id_=behavior['id'],
                    display_name=behavior['display_name']
                )
            else:
                raise ValueError(f"Behavior {node['name']} not found in behavior library")

    return deserialize_node(tree)