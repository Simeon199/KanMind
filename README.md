# KanMind Backend

This is a backend built using Django and Django REST Framework, designed specifically for task management on Kanban boards. It fully supports CRUD operations and serves as the Python equivalent of the Join app's backend.

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [API Testing with Postman](#api-testing-with-postman)
- [Contributing](#contributing)

## Getting Started

1. Clone the repository from GitHub and navigate to the project directory:

```bash
  git clone https://github.com/Simeon199/KanMind.git
  cd KanMind
```

2. Create and activate a virtual environment:

```bash

python -m venv env

# For Windows, activate with:
env\Scripts\activate

# For Linux/mcOS, activate with:
source env/bin/activate
```

3. Install necessary dependencies:

```bash
pip install -r requirements.txt
```

## Prerequisites

To get started with running the application locally, ensure you have the following prerequisites:

- Python 3.12 or higher
- [Postman](https://www.postman.com/downloads/) (optional, for easy API testing)

_All Python dependencies are specified in `requirements.txt` and installed automatically._

## API Testing with Postman

A [Postman Collection](postman/KanMind.postman_collection.json) is included to help you test the API endpoints.

**How to use:**

1. Install Postman and import the collection from `postman/KanMind.postman_collection.json`.
2. Adjust environment variables if necessary (API base URL, tokens, etc.).
3. Use the requests to test and explore API features.

## Contributing

Contributions are always welcome! If you have suggestions for improvements or want to propose changes, please open an issue. Alternatively, consider forking the repository and submitting a pull request.
