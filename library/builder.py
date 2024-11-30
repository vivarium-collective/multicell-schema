import os
import json
from jsonschema import validate, ValidationError
from library.validate_schemas import validate_schema, object_meta_schema, process_meta_schema


class SchemaCreator:
    def __init__(self, schema_type):
        self.schema = {"type": schema_type, "properties": {}, "required": []}
        self.schema_type = schema_type

    def add_property(self, name, property_schema, required=False):
        self.schema["properties"][name] = property_schema
        if required:
            self.schema["required"].append(name)

    def validate(self):
        if self.schema_type == "object":
            validate_schema(self.schema, object_meta_schema)
        elif self.schema_type == "process":
            validate_schema(self.schema, process_meta_schema)
        else:
            raise ValueError("Unsupported schema type")

    def save(self, directory, filename):
        self.validate()
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, filename), 'w') as file:
            json.dump(self.schema, file, indent=4)
        print(f"Schema saved to {os.path.join(directory, filename)}")


# Example usage
if __name__ == '__main__':
    # Create an object schema
    object_creator = SchemaCreator("object")
    object_creator.add_property("id", {"type": "string"}, required=True)
    object_creator.add_property("type", {"type": "string"}, required=True)
    object_creator.add_property("attributes", {"type": "object"}, required=True)
    object_creator.add_property("contained_object_types", {"type": "array"}, required=True)
    object_creator.add_property("boundary_conditions", {"type": "object"}, required=True)
    object_creator.save("schemas/objects", "example_object.json")

    # Create a process schema
    process_creator = SchemaCreator("process")
    process_creator.add_property("id", {"type": "string"}, required=True)
    process_creator.add_property("type", {"type": "string"}, required=True)
    process_creator.add_property("attributes", {"type": "object"}, required=True)
    process_creator.add_property("participating_objects", {"type": "array"}, required=True)
    process_creator.add_property("dynamics", {"type": "object"}, required=True)
    process_creator.save("schemas/processes", "example_process.json")