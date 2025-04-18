import os
import json

from jsonschema import ValidationError
from multicell_utils.validate import validate_schema, object_meta_schema, process_meta_schema
from multicell_utils import pf
from schema import schema_registry
from multicell_utils.registry import project_root
from multicell_utils.graph import create_graph_from_model


class SchemaCreator:
    def __init__(self,
                 schema_type,
                 json_path=None,
                 name=None,
                 inherits_from=None,
                 ):
        inherits_from = inherits_from or []
        if isinstance(inherits_from, str):
            inherits_from = [inherits_from]

        self.schema_type = schema_type
        self.schema = {
            "type": schema_type,
            "inherits_from": inherits_from,
            "attributes": {},
            # "required": []
        }
        if json_path:
            self.load_from_json(json_path, name)

    def add_property(self, name, property_schema, required=False):
        # if name in self.schema:
        #     raise ValueError(f"Property {name} already exists in schema")
        if property_schema is None:
            return

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

    def register(self, overwrite=False):
        try:
            if self.schema_type == "object":
                schema_registry.register_object(self.schema, self.schema["type"], overwrite)
            elif self.schema_type == "process":
                schema_registry.register_process(self.schema, self.schema["type"], overwrite)
        except ValueError as e:
            if not overwrite:
                print(f"Failed to register schema: {e}")
                return
            else:
                print(f"Overwriting schema despite registration failure: {e}")

    def save(self, filename, directory="schema"):
        try:
            self.validate()
        except ValidationError as e:
            raise ValidationError(f"Schema validation failed: {e.message}")

        # make absolute path to directory
        absolute_directory = os.path.join(project_root, directory, self.schema_type) # objects or processes
        local_directory = os.path.join(directory, self.schema_type)
        if not os.path.exists(absolute_directory):
            os.makedirs(absolute_directory)
        with open(os.path.join(absolute_directory, filename), 'w') as file:
            json.dump(self.schema, file, indent=4)
            print(f"Schema saved to {os.path.join(local_directory, filename)}")

    def load_from_json(self, json_path, name):
        assert name is not None, "Name must be provided when loading from JSON"
        with open(json_path, 'r') as file:
            loaded_schema = json.load(file)
        self.schema.update(loaded_schema)
        self.schema["inherits_from"] = json_path
        self.schema["type"] = name


class ObjectCreator(SchemaCreator):
    def __init__(self,
                 type,
                 inherits_from=None,
                 attributes=None,
                 boundary_conditions=None,
                 contained_objects=None,
                 json_path=None
                 ):
        super().__init__("object", json_path, type, inherits_from=inherits_from)
        if contained_objects is not None:
            self.add_property("contained_objects", list(contained_objects))
        if boundary_conditions is not None:
            self.add_property("boundary_conditions", boundary_conditions)
        if attributes is not None:
            self.add_property("attributes", attributes)

        self.schema["type"] = type


class ProcessCreator(SchemaCreator):
    def __init__(self,
                 type,
                 inherits_from=None,
                 attributes=None,
                 participating_objects=None,
                 dynamics=None,
                 json_path=None
                 ):
        super().__init__("process", json_path, inherits_from=inherits_from)
        if dynamics is not None:
            self.add_property("dynamics", dynamics)
        if participating_objects is not None:
            self.add_property("participating_objects", participating_objects)
        if attributes is not None:
            self.add_property("attributes", attributes)
        self.schema["type"] = type

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
    def __init__(self, model_name=None, model_file=None):
        # TODO -- load model with id?
        models_path = 'models'
        if model_file:
            if not model_file.endswith('.json'):
                model_file += '.json'
            model_file = os.path.join(project_root, models_path, model_file)
            with open(model_file, 'r') as file:
                self.model = json.load(file)
        else:
            self.model = {
                "id": make_unique_id(),
                "name": model_name,
                "objects": {},
                "processes": {},
            }

    def __repr__(self):
        # Return a string representation of the model dictionary
        return f"ModelBuilder({pf(self.model)})"

    def validate(self, verbose=True):
        schema_registry.validate_template(self.model)

    def graph(self, filename=None, output_dir='out'):
        return create_graph_from_model(self.model,
                                        filename=filename,
                                        output_dir=output_dir
                                       )

    def specialize(self, path=None, new_type=None):
        if path is None or new_type is None:
            raise ValueError("Must provide both path and new_type for specialization.")

        if not isinstance(path, list) or len(path) != 2:
            raise ValueError("Path must be a list of two elements: ['objects' or 'processes', name]")

        category, name = path
        if category not in ["objects", "processes"]:
            raise ValueError(f"Invalid category '{category}'. Must be 'objects' or 'processes'.")

        if name not in self.model[category]:
            raise KeyError(f"No entry named '{name}' in '{category}'")

        current = self.model[category][name]
        current_type = current.get("type")

        # Check inheritance validity
        if not schema_registry.inherits_from(new_type, current_type):
            raise ValueError(f"Cannot specialize '{current_type}' to '{new_type}': "
                             f"{new_type} does not inherit from {current_type}")

        # Replace the type while keeping the rest of the instance
        specialized = current.copy()
        specialized["type"] = new_type
        self.model[category][name] = specialized
        print(f"Specialized {category[:-1]} '{name}' from '{current_type}' to '{new_type}'")

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

    def save(self, filename, directory="models"):
        try:
            self.validate()
        except ValidationError as e:
            print(f"Model validation failed: {e.message}")
            return

        # make absolute path to directory
        absolute_directory = os.path.join(project_root, directory)
        if not os.path.exists(absolute_directory):
            os.makedirs(absolute_directory)
        with open(os.path.join(absolute_directory, filename), 'w') as file:
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
    demo_model.add_process(name='volume exclusion', process_type='VolumeExclusion', participating_objects='cell')
    demo_model.validate()
    demo_model.save(filename='builder_test.json')

    # TODO: load model from JSON and visualize it


def validate_model_fails(model):
    try:
        model.validate()
    except:
        pass
    else:
        raise AssertionError("Model validation should have failed")


def test_invalid_model():

    # model with object type that does not exist
    demo = ModelBuilder(model_name='demo2')
    demo.add_object(name='universe', object_type='DoesNotExist')
    validate_model_fails(demo)

    # model with object that contains an object type that is not allowed
    demo2 = ModelBuilder(model_name='demo2')
    demo2.add_object(name='cell_field', object_type='CellField', contained_objects=['field'])
    demo2.add_object(name='field', object_type='Field')
    validate_model_fails(demo2)

    # model with process that has an object that does not exist
    demo3 = ModelBuilder(model_name='demo3')
    demo3.add_object(name='cell', object_type='Cell')
    demo3.add_process(name='growth', process_type='CellGrowth', participating_objects='cell2')
    validate_model_fails(demo3)

    # model with process that has an object that is not allowed
    demo4 = ModelBuilder(model_name='demo4')
    demo4.add_object(name='cell', object_type='Cell')
    demo4.add_process(name='diffusion', process_type='Diffusion', participating_objects='cell')
    validate_model_fails(demo4)

def test_model_specialize():
    cell_migration = ModelBuilder(model_name="cell_migration")

    # add objects
    cell_migration.add_object(
        name="universe",
        object_type="Universe",
        contained_objects=[
            "environment"
        ]
    )
    cell_migration.add_object(
        name="environment",
        object_type="MaterialObjectSpace",
        contained_objects=[
            "single_cell",
        ]
    )

    cell_migration.add_object(
        name="single_cell",
        object_type="Cell"
    )

    # add processes
    cell_migration.add_process(
        name="motile force",
        process_type="MotileForce",
        participating_objects=["single_cell"]
    )

    # validate and save generic
    cell_migration.validate()
    cell_migration.save(filename='cell_migration_generic.json')
    cell_migration.graph(filename='cell_migration_generic')

    # specialize the model
    cell_migration.specialize(
        path=['objects', 'single_cell'],
        new_type='CellCPM')

    # validate and save specialized model
    cell_migration.validate()
    cell_migration.save(filename='cell_migration_cpm.json')
    cell_migration.graph(filename='cell_migration_cpm')


if __name__ == '__main__':
    # test_schema_creator()
    # test_invalid_model()
    # test_model_builder()
    test_model_specialize()
