# KanMind Backend

This is a backend built using Django and Django REST Framework, designed specifically for task management on Kanban boards. It fully supports CRUD operations and serves as the Python equivalent of the Join app's backend.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installtion](#installation)
- [Running the Server](#running-the-server)
- [API Testing with Postman](#api-testing-with-postman)
- [Contributing](#contributing)

## Features

- User authentication and board permissions
- CRUD for tasks and boards
- Kanban board management
- RESTful API with DRF

## Prerequisites

To get started with running the application locally, ensure you have the following prerequisites:

- Python 3.12 or higher
- [Postman](https://www.postman.com/downloads/) (optional, for easy API testing)

_All Python dependencies are specified in `requirements.txt` and installed automatically._

## Installation

1. Clone: `git clone clone https://github.com/Simeon199/KanMind.git && cd KanMind`
2. Virtualenv: `python -m venv env && env\Scripts\activate` (Windows)
3. Install: `pip install -r requirements.txt`
4. Migrate: `python manage.py makemigrations && python manage.py migrate`

## Running the Server

`python manage.py runserver`

## API Testing with Postman

A [Postman Collection](postman/KanMind.postman_collection.json) is included to help you test the API endpoints.

**How to use:**

1. Install Postman and import the collection from `postman/KanMind.postman_collection.json`.
2. Set base URL to `http://127.0.0.1:8000/` and adjust further environment variables if necessary.
3. Use the requests to test and explore API features.

## Contributing

Contributions are always welcome! If you have suggestions for improvements or want to propose changes, please open an issue. Alternatively, consider forking the repository and submitting a pull request.
