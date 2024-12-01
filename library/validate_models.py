import os
import json
from jsonschema import validate, ValidationError
from library.validate_schemas import validate_schema, object_meta_schema, process_meta_schema
from schema import schema_registry


def validate_containment(structure):
    for struct, substruct in structure.items():
        # assert struct, substruct relation is valid in schema_registry.allowed_containments
        if struct in schema_registry.allowed_containments:
            pass

        else:
            print(f"Invalid containment: {struct} not found")


# Function to validate a single model
def validate_model(model_path):
    with open(model_path, 'r') as model_file:
        model = json.load(model_file)
        print(f"Validating model: {model['id']}")

        # Validate objects
        for obj_name, obj_schema in model['objects'].items():
            try:
                validate_schema(obj_schema, object_meta_schema, verbose=False)
                print(f"Object '{obj_name}' in model '{model['id']}' is valid.")
            except ValidationError:
                print(f"Object '{obj_name}' in model '{model['id']}' is invalid.")

        # Validate processes
        for proc_name, proc_schema in model['processes'].items():
            try:
                validate_schema(proc_schema, process_meta_schema, verbose=False)
                print(f"Process '{proc_name}' in model '{model['id']}' is valid.")

                # TODO: check processes participating objects' types
                # for obj_name in proc_schema['participating_objects']:
                #     pass

            except ValidationError:
                print(f"Process '{proc_name}' in model '{model['id']}' is invalid.")

        # TODO: Validate containment rules
        validate_containment(model['structure'])


# Function to validate all models in the models directory
def validate_models(models_dir):
    for filename in os.listdir(models_dir):
        if filename.endswith('.json'):
            model_path = os.path.join(models_dir, filename)
            validate_model(model_path)



# Example usage
if __name__ == '__main__':
    # # Validate a specific model
    # validate_model('models/example1.json')

    # Validate all models in the 'models' directory
    validate_models('models')