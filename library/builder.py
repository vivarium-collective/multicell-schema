import os
import json
from jsonschema import validate, ValidationError
from library.validate_schemas import validate_schema, object_meta_schema, process_meta_schema

class SchemaCreator:
    def __init__(self, schema_type):
        self.schema_type = schema_type
        self.schema = {
            "type": schema_type,
            "properties": {},
            "required": []
        }

    def add_property(self, name, property_schema, required=False):
        self.schema[name] = property_schema
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
        try:
            self.validate()
        except ValidationError as e:
            print(f"Schema validation failed: {e.message}")
            return
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, filename), 'w') as file:
            json.dump(self.schema, file, indent=4)
        print(f"Schema saved to {os.path.join(directory, filename)}")


class ObjectCreator(SchemaCreator):
    def __init__(self):
        super().__init__("object")

    def new_type(self, name, attributes={}, boundary_conditions={}, contained_objects=[]):
        self.add_property("type", name)
        self.add_property("attributes", attributes)
        self.add_property("boundary_conditions", boundary_conditions)
        self.add_property("contained_object_types", list(contained_objects))
        self.schema["type"] = name

class ProcessCreator(SchemaCreator):
    def __init__(self):
        super().__init__("process")

    def new_type(self, name, attributes={}, participating_objects=[], dynamics={}):
        self.add_property("type", name)
        self.add_property("attributes", attributes)
        self.add_property("participating_objects", participating_objects)
        self.add_property("dynamics", dynamics)
        self.schema["type"] = name

# Example usage
if __name__ == '__main__':
    # Create an object schema
    object_creator = ObjectCreator()
    object_creator.new_type(
        name="example_object",
        attributes={"size": "integer"},
        boundary_conditions={"condition": "string"},
        contained_objects={"sub_object": "string"}
    )
    object_creator.save("schemas/objects", "example_object.json")

    # Create a process schema
    process_creator = ProcessCreator()
    process_creator.new_type(
        name="example_process",
        attributes={"id": "string", "rate": "number"},
        participating_objects=["object1", "object2"],
        dynamics={"dynamic_property": {}}
    )
    process_creator.save("schemas/processes", "example_process.json")
