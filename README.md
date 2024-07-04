# FastAPI_intern

## Running the application

To run the application, execute the following commands:

    ```bash
    poetry run uvicorn app.main:app --reload

## Running tests

To run the tests, execute the following command:

    ```bash
    poetry run pytest tests/test_main.py

## Running pre-commit hooks

To run all pre-commit hooks on all files, execute the following command:
    
    ```bash
    poetry run pre-commit run --all-files

## Creating Docker Image
    ```bash
    docker build -t my-fastapi-app .

## Running Docker Container
    ```bash
    docker run --env-file .env -p 8000:8000 my-fastapi-app

## View
    http://localhost:8000
