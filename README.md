## Environment Setup

Ensure your environment is ready by following these steps:

1. **Install Poetry**
   - For installation instructions, visit [Poetry's official documentation](https://python-poetry.org/docs/#installation).

2. **Install Dependencies**
   - Run the following command to install required packages:
     ```bash
     poetry install
     ```

3. **Activate Poetry Shell**
   - Activate the poetry shell to ensure dependencies are correctly managed:
     ```bash
     poetry shell
     ```

4. **Database Migration**
   - Set up your database schema with the migration command:
     ```bash
     POSTGRES_URI=postgresql://postgres:postgres@localhost:5432/your_database alembic upgrade head
     ```

## Run Populate Script

To initialize the database with necessary data, execute the populate script:

```bash
python src/init_populate.py
```

## Run app
1. ```bash
   cd src
    ```
2. ```bash
   uvicorn main:app
    ```

## Run ruff
```bash
ruff check . --fix --unsafe-fixes --preview
```