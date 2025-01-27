import os
import json
from jsonschema import validate, ValidationError

# Get the base directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)

# Define paths relative to the project root
object_schemas_dir = os.path.join(project_root, 'schema/object')
process_schemas_dir = os.path.join(project_root, 'schema/process')
templates_dir = os.path.join(project_root, 'schema/templates')
objects_meta_schema_path = os.path.join(project_root, 'schema/metaschema/object_schema.json')
processes_meta_schema_path = os.path.join(project_root, 'schema/metaschema/process_schema.json')
templates_meta_schema_path = os.path.join(project_root, 'schema/metaschema/template_schema.json')

# Load meta-schemas from JSON files
with open(objects_meta_schema_path, 'r') as file:
    object_meta_schema = json.load(file)

with open(processes_meta_schema_path, 'r') as file:
    process_meta_schema = json.load(file)

with open(templates_meta_schema_path, 'r') as file:
    template_meta_schema = json.load(file)


def make_structure(model):
    structure = {}
    for obj_name, obj_schema in model['objects'].items():
        contained_objects = obj_schema.get('contained_objects')
        if contained_objects:
            structure[obj_name] = contained_objects
    return structure


class SchemaRegistry:
    def __init__(self):
        self.object_types = {}
        self.process_types = {}
        self.object_meta_schema = object_meta_schema
        self.process_meta_schema = process_meta_schema
        self.template_meta_schema = template_meta_schema

        # to save allowed object containments with object type as keys
        self.allowed_containments = {}

        # save process-object participation with process type as keys
        self.process_participation = {}

        # save type inheritance with types as keys
        self.object_inheritance = {}
        self.process_inheritance = {}

    def validate_schema(self, schema, meta_schema):
        validate(instance=schema, schema=meta_schema)

    def validate_template(self, model):
        # Validate objects
        for obj_name, obj_schema in model['objects'].items():
            try:
                self.validate_schema(obj_schema, object_meta_schema)
            except ValidationError as e:
                raise ValueError(f"Object '{obj_name}' in model '{model['id']}' is invalid. {e.message}")

            object_type = obj_schema['type']
            assert object_type in self.object_types, f"Object type '{object_type}' is not registered."

            # get containment from object
            contained_objects = obj_schema.get('contained_objects')
            if contained_objects:
                allowed_obj_types = self.allowed_containments[object_type]
                for object_name in contained_objects:
                    assert object_name in model['objects'], f"Contained object '{object_name}' within '{obj_name}' is not in model"
                    contained_object_type = model['objects'][object_name]['type']

                    # check that the object type or its base types are allowed to be contained
                    inherited = self.object_inheritance.get(contained_object_type, [])
                    assert (contained_object_type in allowed_obj_types or
                            any(base_type in allowed_obj_types for base_type in inherited)
                            ), f"Object '{object_name}' is not allowed to be contained by '{obj_name}'"

        # Validate processes
        for proc_name, proc_schema in model['processes'].items():
            process_type = proc_schema['type']
            # process_full_schema = self.process_types[process_type]
            participating_objects_names = proc_schema.get('participating_objects', [])
            participating_objects_types = self.process_types[process_type].get('participating_objects', [])

            # check that participating objects names are in model objects
            for obj_name in participating_objects_names:
                assert obj_name in model['objects'], f"Participating object '{obj_name}' is not valid for process '{proc_name}'"
                obj_type = model['objects'][obj_name]['type']

                # object types that inherit from this type are also allowed
                inherited = self.object_inheritance.get(obj_type, [])
                allowed_obj_types = inherited + [obj_type]

                assert any(obj in participating_objects_types for obj in allowed_obj_types), \
                    (f"None of the allowed object types {allowed_obj_types} are valid for process type '{process_type}' "
                     f"with allowed types {participating_objects_types}")

                # assert allowed_obj_types in participating_objects_types, \
                #     f"Object '{obj_name}' of type '{obj_type}' is not valid for process type '{process_type}' with allowed types {participating_objects_types}"

        # Validate containment structure
        self.validate_containment(model)

    def validate_containment(self, model):
        structure = make_structure(model)
        for parent, children in structure.items():
            parent_type = model['objects'][parent]['type']

            # assert parent object is registered
            assert parent_type in self.object_inheritance, f"Object '{parent}' does not have inheritance information"

            # assert parent object can contain children
            if parent_type not in self.allowed_containments:
                raise ValueError(f"Invalid containment: {parent_type} does not claim contained objects")

            # assert children types can be contained by the parent type
            allowed_children_types = self.allowed_containments[parent_type]
            for child in children:
                child_type = model['objects'][child]['type']
                if child_type not in allowed_children_types:
                    if not any(base_type in allowed_children_types for base_type in self.object_inheritance.get(child_type, [])):
                        print(f"Invalid containment: {child_type} object is not contained by {parent_type}")

    def register_object(self, schema, object_type, overwrite=False):
        if 'type' in schema:
            object_type = schema['type']
        if object_type in self.object_types and not overwrite:
            raise ValueError(f"Object schema '{object_type}' is already registered.")
        try:
            self.validate_schema(schema, self.object_meta_schema)
        except ValidationError as e:
            print(f"Failed to register object schema '{object_type} with metaschema {self.object_meta_schema}': {e.message}")

        self.object_types[object_type] = schema
        # print(f"Object schema '{schema_name}' registered successfully.")

        contained_objects = schema.get('contained_objects')
        if contained_objects:
            if object_type not in self.allowed_containments:
                self.allowed_containments[object_type] = []
            for obj_type in contained_objects:
                self.allowed_containments[object_type].append(obj_type)

        # Register inheritance
        inherits_from = schema.get('inherits_from', [])
        self.object_inheritance[object_type] = inherits_from


    def register_process(self, schema, process_type=None, overwrite=False):
        if 'type' in schema:
            process_type = schema['type']
        if process_type in self.process_types and not overwrite:
            raise ValueError(f"Process schema type '{process_type}' is already registered.")
        try:
            self.validate_schema(schema, self.process_meta_schema)
            self.process_types[process_type] = schema
            # print(f"Process schema '{schema_name}' registered successfully.")
            # if process_name == 'contact_force':
            #     breakpoint()

            participating_objects = schema.get('participating_objects')
            if participating_objects:
                if process_type not in self.process_participation:
                    self.process_participation[process_type] = []
                for object_type in participating_objects:
                    self.process_participation[process_type].append(object_type)

            # Register inheritance
            self.process_inheritance[process_type] = schema.get('inherits_from', [])

        except ValidationError as e:
            print(f"Failed to register process schema '{process_type}': {e.message}")


    def register_template(self, schema, template_name):
        # TODO implement template registration
        schema_name = schema['name']
        pass


def register_schemas_from_directory(directory, register_function):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            schema_path = os.path.join(directory, filename)
            with open(schema_path, 'r') as schema_file:
                try:
                    schema = json.load(schema_file)
                    schema_name = os.path.splitext(filename)[0]
                except Exception as e:
                    print(f"Failed to load schema from file '{filename}': {e}")
                try:
                    register_function(schema, schema_name)
                except Exception as e:
                    print(f"Failed to register schema '{schema_name}' from file '{filename}': {e}")


if __name__ == '__main__':
    from schema import schema_registry

    print("Object schemas:")
    print(schema_registry.objects)
    print("Process schemas:")
    print(schema_registry.processes)
    print("Allowed containments:")
    print(schema_registry.allowed_containments)
    print("Process participation:")
    print(schema_registry.process_participation)
    print("Object inheritance:")
    print(schema_registry.object_inheritance)
    print("Process inheritance:")
    print(schema_registry.process_inheritance)
