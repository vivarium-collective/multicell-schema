import os
import json
from jsonschema import validate, ValidationError
from multicell_utils.validate_schemas import validate_schema, object_meta_schema, process_meta_schema
from schema import schema_registry
from multicell_utils.registry import project_root
from multicell_utils.graph import create_graph_from_model


class SchemaCreator:
    def __init__(self, schema_type, json_path=None, name=None):
        self.schema_type = schema_type
        self.schema = {
            "type": schema_type,
            "properties": {},
            "required": []
        }
        if json_path:
            self.load_from_json(json_path, name)

    def add_property(self, name, property_schema, required=False):
        self.schema[name] = property_schema
        if required:
            self.schema["required"].append(name)

    def validate(self):
        if self.schema_type == "object":
            validate_schema(self.schema, object_meta_schema)
        elif self.schema_type == "process":
            validate_schema(self.schema, process_meta_schema)
        else:
            raise ValueError("Unsupported schema type")

    def save(self, filename, directory="schema", overwrite=False):
        directory = os.path.join(project_root, directory, self.schema_type) # objects or processes
        try:
            self.validate()
        except ValidationError as e:
            print(f"Schema validation failed: {e.message}")
            return

        # Register the schema in the registry
        try:
            if self.schema_type == "object":
                schema_registry.register_object(self.schema["type"], self.schema)
            elif self.schema_type == "process":
                schema_registry.register_process(self.schema["type"], self.schema)
        except ValueError as e:
            if not overwrite:
                print(f"Failed to register schema: {e}")
                return
            else:
                print(f"Overwriting schema despite registration failure: {e}")

        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, filename), 'w') as file:
            json.dump(self.schema, file, indent=4)
        print(f"Schema saved to {os.path.join(directory, filename)}")

    def load_from_json(self, json_path, name):
        assert name is not None, "Name must be provided when loading from JSON"
        with open(json_path, 'r') as file:
            loaded_schema = json.load(file)
        self.schema.update(loaded_schema)
        self.schema["inherits_from"] = json_path
        self.schema["type"] = name


class ObjectCreator(SchemaCreator):
    def __init__(self, name=None, attributes={}, boundary_conditions={}, contained_objects=[], json_path=None):
        super().__init__("object", json_path, name)
        if not json_path:
            self.add_property("type", name)
            self.add_property("attributes", attributes)
            self.add_property("boundary_conditions", boundary_conditions)
            self.add_property("contained_object_types", list(contained_objects))
            self.schema["type"] = name


class ProcessCreator(SchemaCreator):
    def __init__(self, name=None, attributes={}, participating_objects=[], dynamics={}, json_path=None):
        super().__init__("process", json_path)
        if not json_path:
            self.add_property("type", name)
            self.add_property("attributes", attributes)
            self.add_property("participating_objects", participating_objects)
            self.add_property("dynamics", dynamics)
            self.schema["type"] = name


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
def test_schema_creator():
    # Create an object schema
    object_creator = ObjectCreator(
        name="example_object",
        attributes={},
        boundary_conditions={},
        contained_objects=["sub_object"]
    )
    object_creator.validate()
    object_creator.save("example_object.json", overwrite=True)

    # Create a process schema
    process_creator = ProcessCreator(
        name="example_process",
        attributes={"id": "string", "rate": "number"},
        participating_objects=["object1", "object2"],
        dynamics={}
    )
    process_creator.save("example_process.json", overwrite=True)

    # Load a schema from JSON
    object_creator = ObjectCreator(json_path="schema/object/example_object.json", name="example_object2")

    # add to the object schema
    object_creator.add_property("new_property", {"type": "string"})
    object_creator.save("example_object2.json", overwrite=True)
    # print(object_creator.schema)

def test_model_builder():
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

if __name__ == '__main__':
    test_schema_creator()
    test_model_builder()
