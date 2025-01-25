import os
import json
from graphviz import Digraph
from multicell_utils.registry import project_root


def create_graph_from_model(model):
    if isinstance(model, str):
        model_path = os.path.join(project_root, model)
        with open(model_path, 'r') as file:
            model = json.load(file)

    dot = Digraph(comment='Model Graph')

    # Add objects as circles with labels including their types
    for obj_name, obj_data in model['objects'].items():
        label = f"{obj_name}:{obj_data['type']}"
        dot.node(obj_name, label, shape='circle')

    # Add processes as rectangles and connect to participating objects with dashed edges
    for proc_name, proc_data in model['processes'].items():
        label = f"{proc_name}:{proc_data['type']}"
        dot.node(proc_name, label, shape='rectangle')
        for obj in proc_data['participating_objects']:
            dot.edge(obj, proc_name, style='dashed', dir='back')

    # Add containment relations with thicker edges and no arrowhead
    for parent, children in model['structure'].items():
        for child in children:
            dot.edge(parent, child, style='bold', arrowhead='none')

    return dot

# Example usage
if __name__ == "__main__":
    graph = create_graph_from_model('models/example1.json')
    graph.render('../output/model_graph', format='png')

    graph = create_graph_from_model('models/cell_sorting.json')
    graph.render('../output/cell_sorting', format='png')