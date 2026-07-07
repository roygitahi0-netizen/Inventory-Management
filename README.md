# Inventory Management System

A polished Flask-based inventory application with a REST API, a CLI, and automated tests. It supports creating, viewing, updating, deleting, and searching inventory items, and it can also look up product details from an external product API.

## Highlights

- RESTful inventory endpoints
- Search by name and barcode
- Filtering by category and price
- Barcode import workflow
- CLI for everyday inventory actions
- Local SQLite storage for development

## Project structure

- [app.py](app.py): Flask application and API routes
- [models.py](models.py): SQLite repository layer
- [external_api.py](external_api.py): external product lookup helpers
- [cli/cli.py](cli/cli.py): command-line interface
- [tests](tests): unit and integration tests

## Quick start

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install flask requests pytest
   ```

4. Start the server:

   ```bash
   python app.py

## API overview

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

## CLI usage

Run the interactive CLI with:

```bash
python cli/cli.py
```

## Testing

Run the full test suite with:

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

## Notes

The app uses a local SQLite database file named inventory.db. It is created automatically on first run and is intended for local development and testing.

