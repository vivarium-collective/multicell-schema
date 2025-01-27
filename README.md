# Project Overview

This project contains models and schemas for validating and building JSON schemas for objects and processes.

**Note: This project is still in development.**

## Notebooks
* [Demo](https://vivarium-collective.github.io/multicell-schema/notebooks/demo.html)
* [Demo 2](https://vivarium-collective.github.io/multicell-schema/notebooks/demo2.html)
* [Cell Sorting](https://vivarium-collective.github.io/multicell-schema/notebooks/cell_sorting.html)

## Directory Structure

- `models/`: Contains JSON files defining various models.

- `schemas/`: Contains JSON schema files for objects, processes, and meta-schemas.
  - `objects/`: Contains object schema files.
  - `processes/`: Contains process schema files.
  - `templates/`: Contains template schema files.
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
