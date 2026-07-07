# Inventory Management System

A simple Flask-based inventory app with a REST API, a CLI, and automated tests. It lets you create, view, update, delete, and search inventory items, and it can also look up product details from an external product API.

## Features

- CRUD endpoints for inventory items
- Search by name and barcode
- Filtering by category and price
- Barcode import workflow
- CLI for common inventory actions
- SQLite database persistence

## Project structure

- app.py: Flask application and API routes
- models.py: SQLite repository layer
- external_api.py: external product lookup helpers
- cli/cli.py: command-line interface
- tests/: unit and integration tests

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install flask requests pytest
   ```

4. Start the app:

   ```bash
   python app.py
   ```

   The API will be available at http://127.0.0.1:5000.

## Usage

### API

- GET /api/health
- GET /api/inventory
- POST /api/inventory
- GET /api/inventory/<id>
- PATCH /api/inventory/<id>
- DELETE /api/inventory/<id>
- GET /api/inventory/search?q=...
- GET /api/external/barcode/<barcode>
- GET /api/external/search?q=...
- POST /api/inventory/import/barcode

### CLI

Run:

```bash
python cli/cli.py
```

## Testing

Run the test suite with:

```bash
python -m pytest -q
```

## Pull request workflow

This project uses feature branches for isolated work. The recommended flow is:

1. Create a branch from main.
2. Make focused changes.
3. Open a pull request into main.
4. Merge after review and passing tests.
5. Delete the merged branch.

A full workflow guide is available in [PR_WORKFLOW.md](PR_WORKFLOW.md).

## Notes

The app uses a local SQLite database file named inventory.db. It is created automatically on first run and is intended for local development and testing.

