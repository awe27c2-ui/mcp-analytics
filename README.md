# MCP Analytics Sample Project

This project is a lightweight analytics sandbox that exposes curated datasets through an MCP (Model Context Protocol) server backed by DuckDB. It is designed to demonstrate how a small, well-described data catalog can be paired with safe, queryable access so AI agents or humans can explore data using natural language prompts that translate into SQL.

## Use Case

The core use case is to provide a minimal, end-to-end example of:

- **Curated datasets** with descriptions, schemas, and example questions.
- **Safe query execution** that restricts access to read-only SELECT statements and enforces result limits.
- **A reproducible demo database** that can be generated locally with synthetic data.

This makes it easy to prototype an AI-assisted analytics experience where a user can ask questions, the agent inspects the catalog, and then runs safe queries against the dataset.

## Project Structure

- `server.py`: MCP server that publishes a dataset catalog and provides tools to list datasets, describe schemas, and execute safe SQL queries.
- `setup_db.py`: Script to generate a DuckDB database with synthetic `subscriptions` and `events` tables.

## Quick Start

1. Create the sample database:
   ```bash
   python setup_db.py
   ```

2. Run the MCP server:
   ```bash
   python server.py
   ```

## Example Workflow

1. Call `list_datasets` to discover available datasets.
2. Call `describe_dataset` for schemas and example questions.
3. Use `run_query` to execute a safe SELECT query with a default limit.
