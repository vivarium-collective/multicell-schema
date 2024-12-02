import os
import json
from graphviz import Digraph
from registry import project_root


def create_graph_from_model(model_path):

    # add to project_root
    model_path = os.path.join(project_root, model_path)


    with open(model_path, 'r') as file:
        model = json.load(file)

    dot = Digraph(comment='Model Graph')

    # Add objects as circles
    for obj_name, obj_data in model['objects'].items():
        dot.node(obj_name, obj_name, shape='circle')

    # Add processes as rectangles and connect to participating objects
    for proc_name, proc_data in model['processes'].items():
        dot.node(proc_name, proc_name, shape='rectangle')
        for obj in proc_data['participating_objects']:
            dot.edge(proc_name, obj)

    # Add containment relations
    for parent, children in model['structure'].items():
        for child in children:
            dot.edge(parent, child)

    return dot

# Example usage
if __name__ == "__main__":
    graph = create_graph_from_model('models/example1.json')
    graph.render('../output/model_graph', format='png')