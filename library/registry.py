import os
import json
from jsonschema import validate, ValidationError

# Load meta-schemas from JSON files
with open('schemas/metaschema/object_schema.json', 'r') as file:
    object_meta_schema = json.load(file)

with open('schemas/metaschema/process_schema.json', 'r') as file:
    process_meta_schema = json.load(file)


class SchemaRegistry:
    def __init__(self):
        self.objects = {}
        self.processes = {}
        self.object_meta_schema = object_meta_schema
        self.process_meta_schema = process_meta_schema

        # TODO: need to save allowed object containments
        # self.allowed_containments = {}

        # TODO: need to save type inheritance
        # self.type_inheritance = {}

    def validate_schema(self, schema, meta_schema):
        validate(instance=schema, schema=meta_schema)

    def register_object(self, schema_name, schema):
        try:
            self.validate_schema(schema, self.object_meta_schema)
            self.objects[schema_name] = schema
            print(f"Object schema '{schema_name}' registered successfully.")

            # contained_object_types = schema.get('contained_object_types')
            # if contained_object_types:
            #     for obj_type in contained_object_types:
            #         if obj_type not in self.allowed_containments:
            #             self.allowed_containments[obj_type] = []
            #         self.allowed_containments[obj_type].append(schema_name)

        except ValidationError as e:
            print(f"Failed to register object schema '{schema_name}': {e.message}")

    def register_process(self, schema_name, schema):
        try:
            self.validate_schema(schema, self.process_meta_schema)
            self.processes[schema_name] = schema
            print(f"Process schema '{schema_name}' registered successfully.")
        except ValidationError as e:
            print(f"Failed to register process schema '{schema_name}': {e.message}")

    def get_object_schema(self, schema_name):
        return self.objects.get(schema_name)

    def get_process_schema(self, schema_name):
        return self.processes.get(schema_name)
