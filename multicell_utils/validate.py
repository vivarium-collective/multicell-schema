import os
import json
from jsonschema import validate, ValidationError
from schema import schema_registry
from multicell_utils.registry import (
    object_schemas_dir, process_schemas_dir, templates_dir,
    object_meta_schema, process_meta_schema, template_meta_schema
)



# Function to validate a schema against a meta-schema
def validate_schema(schema, meta_schema):
    try:
        validate(instance=schema, schema=meta_schema)
        print(f"Schema {schema.get('type', schema.get('name', schema.get('id')))} is valid.")
    except ValidationError as e:
        schema_repr = schema.get('type', schema.get('name', schema.get('id')))


        print(f"Schema {schema_repr}: is invalid: \n {e.message}")


# Function to load and validate schemas from a directory
def validate_schemas_from_directory(directory, meta_schema):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            schema_path = os.path.join(directory, filename)
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
                try:
                    validate_schema(schema, meta_schema)
                except Exception as e:
                    print(f"Error validating schema file {schema_file}: {e}")


# Function to load and validated templates from a directory
def validate_templates_from_directory(directory, meta_schema):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            template_path = os.path.join(directory, filename)
            with open(template_path, 'r') as template_file:
                template = json.load(template_file)
                try:
                    validate_schema(template, meta_schema)
                except Exception as e:
                    print(f"Error validating template file {template_file}: {e}")


def test_validate_schema():
    # Validate object schemas
    validate_schemas_from_directory(object_schemas_dir, object_meta_schema)

    # Validate process schemas
    validate_schemas_from_directory(process_schemas_dir, process_meta_schema)

    # Validate templates
    validate_templates_from_directory(templates_dir, template_meta_schema)


if __name__ == '__main__':
    # Validate object schemas
    print("VALIDATING SCHEMAS")
    test_validate_schema()
