# Project Overview

This project contains models and schemas for validating and building JSON schemas for objects and processes.

**Note: This project is still in development.**

## Notebooks
* [Demo](https://vivarium-collective.github.io/multicell-schema/notebooks/demo.html)
* [Cell Sorting](https://vivarium-collective.github.io/multicell-schema/notebooks/cell_sorting.html)

## Directory Structure

- `models/`: Contains JSON files defining various models.
  - `example1.json`: Example model file.
  - `specific_model.json`: Specific model file.

- `schemas/`: Contains JSON schema files for objects, processes, and meta-schemas.
  - `objects/`: Contains object schema files.
    - `example_object.json`: Example object schema.
    - `field_base.json`: Base schema for field objects.
  - `processes/`: Contains process schema files.
    - `example_process.json`: Example process schema.
  - `templates/`: Contains template schema files.
    - `example_template.json`: Example template schema.
  - `metaschema/`: Contains meta-schema files.
    - `basic_schema.json`: Basic schema types such as units.
    - `object_schema.json`: Meta-schema for object validation.
    - `process_schema.json`: Meta-schema for process validation.
    - `template_schema.json`: Meta-schema for template validation.

- `multicell_utils/`: Contains Python scripts for schema validation and building.
  - `validate.py`: Scripts for validating schemas and models.
  - `registry.py`: Scripts for managing schema directories and meta-schemas.
  - `builder.py`: Builder tools for building schemas and models with a Python API.
  - `graph.py`: Scripts for generating a graph figure of object and process dependencies.


### Validating Models