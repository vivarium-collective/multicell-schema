import os
import json
from jsonschema import validate, ValidationError

# Load meta-schemas from JSON files
with open('schemas/metaschema/object_schema.json', 'r') as file:
    object_meta_schema = json.load(file)

with open('schemas/metaschema/process_schema.json', 'r') as file:
    process_meta_schema = json.load(file)

# Function to validate a schema against a meta-schema
def validate_schema(schema, meta_schema):
    try:
        validate(instance=schema, schema=meta_schema)
        print(f"Schema {schema['id']} is valid.")
    except ValidationError as e:
        print(f"Schema {schema['id']} is invalid: {e.message}")

# Function to load and validate schemas from a directory
def validate_schemas_from_directory(directory, meta_schema):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            schema_path = os.path.join(directory, filename)
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
                validate_schema(schema, meta_schema)

# Validate object schemas
validate_schemas_from_directory('schemas/objects', object_meta_schema)

# Validate process schemas
validate_schemas_from_directory('schemas/processes', process_meta_schema)