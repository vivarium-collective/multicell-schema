class SchemaRegistry:
    def __init__(self):
        self.objects = {}
        self.processes = {}

    def register_object(self, schema_name, schema):
        self.objects[schema_name] = schema

    def register_process(self, schema_name, schema):
        self.processes[schema_name] = schema

    def get_object_schema(self, schema_name):
        return self.objects.get(schema_name)

    def get_process_schema(self, schema_name):
        return self.processes.get(schema_name)
