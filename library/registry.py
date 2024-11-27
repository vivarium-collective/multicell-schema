import os
import json
from jsonschema import validate, ValidationError


class SchemaRegistry:
    def __init__(self):
        self.objects = {}
        self.processes = {}

        # Load meta-schemas from JSON files
        with open('schemas/metaschema/object_schema.json', 'r') as file:
            self.object_meta_schema = json.load(file)

        with open('schemas/metaschema/process_schema.json', 'r') as file:
            self.process_meta_schema = json.load(file)

    def validate_schema(self, schema, meta_schema):
        validate(instance=schema, schema=meta_schema)

    def register_object(self, schema_name, schema):
        try:
            self.validate_schema(schema, self.object_meta_schema)
            self.objects[schema_name] = schema
            print(f"Object schema '{schema_name}' registered successfully.")
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
