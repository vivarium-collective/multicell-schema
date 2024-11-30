import os
import json
from jsonschema import validate, ValidationError
from library.registry import (
    object_schemas_dir, process_schemas_dir, object_meta_schema, process_meta_schema)


# Function to validate a schema against a meta-schema
def validate_schema(schema, meta_schema, verbose=True):
    try:
        validate(instance=schema, schema=meta_schema)
        if verbose:
            print(f"Schema {schema['id']} is valid.")
    except ValidationError as e:
        if verbose:
            print(f"Schema {schema['id']} is invalid: {e.message}")

# Function to load and validate schemas from a directory
def validate_schemas_from_directory(directory, meta_schema):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            schema_path = os.path.join(directory, filename)
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
                validate_schema(schema, meta_schema)


if __name__ == '__main__':
    # Validate object schemas
    validate_schemas_from_directory(object_schemas_dir, object_meta_schema)

    # Validate process schemas
    validate_schemas_from_directory(process_schemas_dir, process_meta_schema)
