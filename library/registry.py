import os
import json
from jsonschema import validate, ValidationError

object_schemas_dir = 'schemas/objects'
process_schemas_dir = 'schemas/processes'
objects_meta_schema_path = 'schemas/metaschema/object_schema.json'
processes_meta_schema_path = 'schemas/metaschema/process_schema.json'

# Load meta-schemas from JSON files
with open(objects_meta_schema_path, 'r') as file:
    object_meta_schema = json.load(file)

with open(processes_meta_schema_path, 'r') as file:
    process_meta_schema = json.load(file)


class SchemaRegistry:
    def __init__(self):
        self.objects = {}
        self.processes = {}
        self.object_meta_schema = object_meta_schema
        self.process_meta_schema = process_meta_schema

        # to save allowed object containments
        self.allowed_containments = {}

        # save process-object participation
        self.process_participation = {}

        # to save type inheritance
        # self.type_inheritance = {}

    def validate_schema(self, schema, meta_schema):
        validate(instance=schema, schema=meta_schema)

    def register_object(self, schema_name, schema):
        try:
            self.validate_schema(schema, self.object_meta_schema)
            self.objects[schema_name] = schema
            print(f"Object schema '{schema_name}' registered successfully.")

            contained_object_types = schema.get('contained_object_types')
            if contained_object_types:
                if schema_name not in self.allowed_containments:
                    self.allowed_containments[schema_name] = []
                for obj_type in contained_object_types:
                    self.allowed_containments[schema_name].append(obj_type)

        except ValidationError as e:
            print(f"Failed to register object schema '{schema_name}': {e.message}")

    def register_process(self, schema_name, schema):
        try:
            self.validate_schema(schema, self.process_meta_schema)
            self.processes[schema_name] = schema
            print(f"Process schema '{schema_name}' registered successfully.")

            participating_objects = schema.get('participating_objects')
            if participating_objects:
                if schema_name not in self.process_participation:
                    self.process_participation[schema_name] = []
                for obj_type in participating_objects:
                    self.process_participation[schema_name].append(obj_type)

        except ValidationError as e:
            print(f"Failed to register process schema '{schema_name}': {e.message}")

    def get_object_schema(self, schema_name):
        return self.objects.get(schema_name)

    def get_process_schema(self, schema_name):
        return self.processes.get(schema_name)


def register_schemas_from_directory(directory, register_function):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            schema_path = os.path.join(directory, filename)
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
                schema_name = os.path.splitext(filename)[0]
                register_function(schema_name, schema)


if __name__ == '__main__':
    from schemas import schema_registry

    print("Object schemas:")
    print(schema_registry.objects)
    print("Process schemas:")
    print(schema_registry.processes)
    print("Allowed containments:")
    print(schema_registry.allowed_containments)
    print("Process participation:")
    print(schema_registry.process_participation)
