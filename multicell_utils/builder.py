import os
import json

from jsonschema import ValidationError
from multicell_utils.validate import validate_schema, object_meta_schema, process_meta_schema
from multicell_utils import pf
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
    def __init__(self,
                 name=None,
                 attributes=None,
                 boundary_conditions=None,
                 contained_objects=None,
                 json_path=None
                 ):
        super().__init__("object", json_path, name)
        if contained_objects is None:
            contained_objects = []
        if boundary_conditions is None:
            boundary_conditions = {}
        if attributes is None:
            attributes = {}
        if not json_path:
            self.add_property("type", name)
            self.add_property("attributes", attributes)
            self.add_property("boundary_conditions", boundary_conditions)
            self.add_property("contained_objects", list(contained_objects))
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

def make_unique_id():
    models_dir = os.path.join(project_root, 'models')
    existing_ids = []

    if os.path.exists(models_dir):
        for filename in os.listdir(models_dir):
            if filename.endswith('.json'):
                with open(os.path.join(models_dir, filename), 'r') as file:
                    try:
                        model = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Error loading model from {filename}")
                        continue
                    existing_ids.append(model['id'])

    max_id = 0
    for model_id in existing_ids:
        if model_id.startswith('model_'):
            try:
                num = int(model_id.split('_')[1])
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

    new_id = f"model_{max_id + 1:06d}"
    return new_id

class ModelBuilder:
    def __init__(self, model_name, id=None):
        # TODO load a base model from JSON

        self.model = {
            "id": id or make_unique_id(),
            "name": model_name,
            "objects": {},
            "processes": {},
            "structure": {}
        }


    def __repr__(self):
        # Return a string representation of the model dictionary
        return f"ModelBuilder({pf(self.model)})"

    def verify(self, verbose=True):
        schema_registry.validate_template(self.model)
        print("Model verification successful.")

    def graph(self):
        return create_graph_from_model(self.model)

    def add_object(self,
                   name,
                   object_type,
                   attributes=None,
                   boundary_conditions=None,
                   contained_objects=None
                   ):
        if contained_objects is None:
            contained_objects = []
        if boundary_conditions is None:
            boundary_conditions = {}
        if attributes is None:
            attributes = {}

        self.model["objects"][name] = {
            "type": object_type,
            "attributes": attributes,
            "boundary_conditions": boundary_conditions,
            "contained_objects": contained_objects
        }

    def add_process(self,
                    name,
                    process_type,
                    participating_objects=None,
                    attributes=None
                    ):
        if attributes is None:
            attributes = {}
        if participating_objects is None:
            participating_objects = []
        elif isinstance(participating_objects, str):
            participating_objects = [participating_objects]
        assert isinstance(participating_objects, list), "Participating objects must be a list or string"

        self.model["processes"][name] = {
            "type": process_type,
            "attributes": attributes,
            "participating_objects": participating_objects
        }

    # def link_containment(self, parent_name, child_name):
    #     if parent_name not in self.model["structure"]:
    #         self.model["structure"][parent_name] = []
    #     self.model["structure"][parent_name].append(child_name)

    # def link_object(self, process_name, object_name):
    #     if process_name in self.model["processes"]:
    #         self.model["processes"][process_name]["participating_objects"].append(object_name)

    def save(self, filename, directory="models"):

        try:
            self.verify()
        except ValidationError as e:
            print(f"Model validation failed: {e.message}")
            return

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
        contained_objects=["sub_object"]
    )
    object_creator.validate()
    object_creator.save("example_object.json", overwrite=True)

    # Create a process schema
    process_creator = ProcessCreator(
        name="example_process",
        attributes={"id": "string", "rate": "number"},
        participating_objects=["object1", "object2"],
    )
    process_creator.save("example_process.json", overwrite=True)

    # Load a schema from JSON
    object_creator = ObjectCreator(json_path="schema/object/example_object.json", name="example_object2")

    # add to the object schema
    object_creator.add_property("new_property", {"type": "string"})
    object_creator.save("example_object2.json", overwrite=True)
    # print(object_creator.schema)




def test_model_builder():
    demo_model = ModelBuilder(model_name='demo')
    demo_model.add_object(name='universe', object_type='Universe', contained_objects=['cell field', 'chemical field'])
    demo_model.add_object(name='chemical field', object_type='Field')
    demo_model.add_object(name='cell field', object_type='CellField', contained_objects=['cell'])
    demo_model.add_object(name='cell', object_type='Cell')
    demo_model.add_process(name='growth', process_type='CellGrowth', participating_objects='cell')
    demo_model.add_process(name='diffusion', process_type='Diffusion', participating_objects='chemical field')
    demo_model.add_process(name='volume exclusion', process_type='VolumeExclusion', participating_objects='cell field')
    demo_model.verify()
    demo_model.save(filename='builder_test.json')

    # TODO: load model from JSON and visualize it

if __name__ == '__main__':
    # test_schema_creator()
    test_model_builder()
