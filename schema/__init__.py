from multicell_utils.registry import SchemaRegistry, object_schemas_dir, \
    process_schemas_dir, register_schemas_from_directory

# Create an instance of SchemaRegistry
schema_registry = SchemaRegistry()

# Register object schemas
register_schemas_from_directory(object_schemas_dir, schema_registry.register_object)

# Register process schemas
register_schemas_from_directory(process_schemas_dir, schema_registry.register_process)
