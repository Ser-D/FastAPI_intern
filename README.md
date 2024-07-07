# Увага
# Attention
# Achtung

Commands to run the application

    ```bash
    docker-compose up -d
    poetry run uvicorn app.main:app --reload 

Running the application image through Docker

    ```bash
    docker-compose -f docker-compose.nonlocal.yml up --build


------------------------------------------------------------
# FastAPI_intern

## Running the application

To run the application, execute the following commands:

    ```bash
    poetry run uvicorn app.main:app --reload
    ENV=local poetry run uvicorn app.main:app --reload
    docker-compose -f docker-compose.nonlocal.yml up --build



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

## Running the application with Docker Compose

To run the application with Docker Compose, execute the following commands:

### Build and start the containers:    
    ```bash
    docker-compose up --build
    docker-compose up -d
    docker-compose -f docker-compose.local.yml up -d
    docker-compose -f docker-compose.nonlocal.yml up --build


### Stop the containers:
    ```bash
    docker-compose down

## View the applicationView
After starting the application, you can view it in your browser at:
    http://localhost:8000

## Health Check
You can check the health of the application and its database connections by accessing the following endpoints:

Application health check: http://localhost:8000/docs#/

Database connection health check: http://localhost:8000/healthchecker

# Database Migrations

## Creating Migrations

    ```bash
    alembic init migratin

Configuration of env.py and alembic.ini

    ```bash
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head



-----------------------
docker-compose -f docker-compose.local.yml up -d

redis.exceptions.ConnectionError: Error 8 connecting to redis:6379. 8.
