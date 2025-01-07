import os
import json
from library.graph import create_graph_from_model


class ModelBuilder:
    def __init__(self, model_name):
        self.model = {
            "id": model_name,
            "name": model_name,
            "objects": {},
            "processes": {},
            "structure": {}
        }

    def add_object(self, name, obj_type, attributes={}, boundary_conditions={}, contained_objects=[]):
        self.model["objects"][name] = {
            "type": obj_type,
            "attributes": attributes,
            "boundary_conditions": boundary_conditions
        }
        if contained_objects:
            self.model["structure"][name] = contained_objects

    def add_process(self, name, proc_type, attributes={}, participating_objects=[]):
        self.model["processes"][name] = {
            "type": proc_type,
            "attributes": attributes,
            "participating_objects": participating_objects
        }

    def link_containment(self, parent, child):
        if parent not in self.model["structure"]:
            self.model["structure"][parent] = []
        self.model["structure"][parent].append(child)

    def link_participation(self, process, obj):
        if process in self.model["processes"]:
            self.model["processes"][process]["participating_objects"].append(obj)

    def save(self, filename, directory="models"):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, filename), 'w') as file:
            json.dump(self.model, file, indent=4)
        print(f"Model saved to {os.path.join(directory, filename)}")


# Example usage
if __name__ == '__main__':
    model_creator = ModelBuilder("creator_example1")

    # Add objects
    model_creator.add_object("cell_field", "CPMCellField", attributes={"bounds": {"x": 100, "y": 100, "z": 100}})
    model_creator.add_object("cells", "CellPopulation", attributes={"species": ["A", "B"]})
    model_creator.add_object("field", "Field", attributes={"molecular_species": ["X", "Y"]})

    # Add process
    model_creator.add_process("contact_force", "ContactForce", attributes={"contact_energy_matrix": [[1, 2], [2, 1]]}, participating_objects=["cell_field"])

    # Link containment
    model_creator.link_containment("cell_field", "cells")

    # Save model
    model_creator.save("creator_example1.json")

    # Graph model
    graph = create_graph_from_model('models/creator_example1.json')
    graph.render('output/creator_example1', format='png')

    # TODO: load model from JSON and visualize it