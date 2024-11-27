import os
import json
from library.registry import SchemaRegistry, object_meta_schema, process_meta_schema

# Create an instance of SchemaRegistry
schema_registry = SchemaRegistry()

# Define the directories containing the schemas
object_schemas_dir = 'schemas/objects'
process_schemas_dir = 'schemas/processes'

# Function to load and register schemas from a directory
def register_schemas_from_directory(directory, register_function):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            schema_path = os.path.join(directory, filename)
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
                schema_name = os.path.splitext(filename)[0]
                register_function(schema_name, schema)

# Register object schemas
register_schemas_from_directory(object_schemas_dir, schema_registry.register_object)

# Register process schemas
register_schemas_from_directory(process_schemas_dir, schema_registry.register_process)
