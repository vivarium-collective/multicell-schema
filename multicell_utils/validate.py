import os
import json
from jsonschema import validate, ValidationError
from schema import schema_registry
from multicell_utils.registry import (
    object_schemas_dir, process_schemas_dir, templates_dir,
    object_meta_schema, process_meta_schema, template_meta_schema
)


def validate_containment(model):
    structure = model['structure']
    for parent, children in structure.items():
        parent_type = model['objects'][parent]['type']

        assert parent_type in schema_registry.object_inheritance, f"Object '{parent}' does not have inheritance information"

        if parent_type not in schema_registry.allowed_containments:
            print(f"Invalid containment: {parent_type} not found in allowed containments")
            continue

        allowed_children = schema_registry.allowed_containments[parent_type]
        for child in children:
            child_type = model['objects'][child]['type']
            if child_type not in allowed_children:
                # Check inheritance
                if not any(base_type in allowed_children for base_type in schema_registry.object_inheritance.get(child_type, [])):
                    print(f"Invalid containment: {child_type} is not allowed within {parent_type}")


# Function to validate a single model
def validate_model(model_path):
    with open(model_path, 'r') as model_file:
        model = json.load(model_file)
        print(f"Validating model: {model['id']}")

        # Validate objects
        for obj_name, obj_schema in model['objects'].items():
            try:
                validate_schema(obj_schema, object_meta_schema)
            except ValidationError as e:
                print(f"Object '{obj_name}' in model '{model['id']}' is invalid.")

        # Validate processes
        for proc_name, proc_schema in model['processes'].items():
            try:
                validate_schema(proc_schema, process_meta_schema)

                # TODO: check processes participating objects' types
                # for obj_name in proc_schema['participating_objects']:
                #     pass

            except ValidationError as e:
                print(f"Process '{proc_name}' in model '{model['id']}' is invalid.")

        # TODO: Validate containment rules
        validate_containment(model)


# Function to validate all models in the models directory
def validate_models(models_dir):
    for filename in os.listdir(models_dir):
        if filename.endswith('.json'):
            model_path = os.path.join(models_dir, filename)
            try:
                validate_model(model_path)
            except Exception as e:
                print(f"Error validating model {model_path}: {e}")


# Function to validate a schema against a meta-schema
def validate_schema(schema, meta_schema):
    try:
        validate(instance=schema, schema=meta_schema)
        print(f"Schema {schema['type']} is valid.")
    except ValidationError as e:
        print(f"Schema {schema['type']} is invalid")


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
                    print(f"Error validating schema {schema['type']}: {e}")


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
                    print(f"Error validating template {template['id']}: {template['name']}: {e}")


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

    # # Validate a specific model
    # validate_model('models/example1.json')

    # Validate all models in the 'models' directory
    print("VALIDATING MODELS")
    validate_models('models')
