# Project Overview

This project contains models and schemas for validating and building JSON schemas for objects and processes.

**Note: This project is still in development.**

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
  - `metaschema/`: Contains meta-schema files.
    - `process_schema.json`: Meta-schema for process validation.

- `library/`: Contains Python scripts for schema validation and building.
  - `validate_schemas.py`: Script for validating schemas.
  - `validate_models.py`: Script for validating models.
  - `registry.py`: Script for managing schema directories and meta-schemas.
  - `builder.py`: Script for building schemas using a Python API.
  - `graph.py`: Script for generating a graph figure of object and process dependencies in a multicell model.

- `basic_schema.json`: Defines basic types, including arrays and units.

## Usage

### Validating Models