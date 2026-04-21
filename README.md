# KanMind Backend

This is a backend built using Django and Django REST Framework, designed specifically for task management on Kanban boards. It fully supports CRUD operations and serves as the Python equivalent of the KanMind app's backend. The respective frontend repository can be found under the following link:
[KanMind Frontend](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Guest Login](#guest-login)
- [Creating a Superuser](#creating-a-superuser)
- [Running the Tests](#running-the-tests)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- User registration and token-based authentication
- Guest login with pre-seeded demo account
- CRUD for tasks and boards
- Kanban board management (To-Do, In Progress, Review, Done)
- Comment system on tasks
- Role-based access control (board owner vs. member)
- RESTful API with Django REST Framework
- Comprehensive pytest test suite (auth, boards, tasks)

## Prerequisites

To get started with running the application locally, ensure you have the following:

- Python 3.12 or higher

_All Python dependencies are specified in `requirements.txt` and installed automatically._

## Installation

1. Clone: `git clone https://github.com/Simeon199/KanMind.git && cd KanMind`
2. Virtualenv: `python -m venv env && env\Scripts\activate` (Windows)
3. Install: `pip install -r requirements.txt`
4. Migrate: `python manage.py makemigrations && python manage.py migrate`
5. The guest demo account is seeded automatically by the migration in step 4.

## Running the Server

To start the development server:

1. Run: `python manage.py runserver`
2. Access the API at `http://127.0.0.1:8000/` in your browser or API client.

This launches Django's built-in development server, allowing you to test the API endpoints locally. Note that this is for development only.

## Guest Login

A pre-seeded guest account is available for quick exploration of the API without registration. It is created automatically when you run `python manage.py migrate`, so no extra step is needed.

Log in with:

```json
POST /api/login/
{
  "email": "kevin@kovacsi.de",
  "password": "asdasdasd"
}
```

The response contains an authentication token that can be used as a Bearer token for all subsequent requests.

## Creating a Superuser

To access admin features or perform administrative tasks, create a superuser account:

1. Run `python manage.py createsuperuser`
2. Follow the prompts to enter a username, email, and password.
3. Use the superuser credentials to log in via the Django admin panel at `http://127.0.0.1:8000/admin/` or for API authentication.

This is useful for testing permissions, managing users, and accessing protected endpoints.

## Running the Tests

The project uses **pytest** with **pytest-django** for all automated tests. To run the full test suite:

```
python -m pytest
```

To run tests for a specific app:

```
python -m pytest auth_app/tests/ -v
python -m pytest board_app/tests/ -v
python -m pytest tasks_app/tests/ -v
```

The test suite covers authentication flows, board and task CRUD, comment endpoints, permission classes, and serializer validation.

## Project Structure

```
KanMind/
├── core/                        # Django project configuration
│   ├── settings.py              # Global settings (apps, auth, CORS, DRF)
│   ├── urls.py                  # Root URL dispatcher
│   ├── wsgi.py                  # WSGI entry point
│   └── asgi.py                  # ASGI entry point
│
├── auth_app/                    # User registration & authentication
│   ├── models.py                # UserProfile model
│   ├── api/
│   │   ├── views.py             # RegistrationView, CustomLoginView
│   │   ├── serializers.py       # RegistrationSerializer, CustomAuthTokenSerializer
│   │   └── urls.py              # /api/registration/, /api/login/
│   ├── management/
│   │   └── commands/
│   │       └── create_guest_user.py  # Seeds the demo guest account
│   └── tests/                   # pytest tests for auth endpoints & serializers
│
├── board_app/                   # Kanban board management
│   ├── models.py                # Board model (owner, members)
│   ├── api/
│   │   ├── views.py             # BoardView, BoardRetrieveUpdateDestroyView, EmailCheckView
│   │   ├── serializers.py       # BoardSerializer, SingleBoardSerializer
│   │   ├── permissions.py       # OwnerOfBoardPermission
│   │   └── urls.py              # /api/boards/, /api/boards/<id>/, /api/email-check/
│   └── tests/                   # pytest tests for board endpoints, permissions & serializers
│
├── tasks_app/                   # Task & comment management
│   ├── models.py                # Task model, TaskCommentsModel
│   ├── api/
│   │   ├── views.py             # TaskListCreateView, TaskRetrieveUpdateDestroyView,
│   │   │                        # TaskCommentListView, TasksAssignedOrReviewedView
│   │   ├── serializers.py       # TaskSerializer, TaskCommentsSerializer
│   │   ├── permissions.py       # IsMemberOfBoard, IsTaskCreatorOrBoardOwner, IsCommentAuthor
│   │   └── urls.py              # /api/tasks/**, /api/tasks/<id>/comments/**
│   └── tests/                   # pytest tests for task/comment endpoints, permissions & serializers
│
├── pytest.ini                   # pytest configuration
├── manage.py                    # Django CLI entry point
├── requirements.txt             # Python dependencies
└── db.sqlite3                   # SQLite database (development)
```

The project follows a **per-app API module pattern**: each Django app (`auth_app`, `board_app`, `tasks_app`) contains an `api/` sub-package with its own `views.py`, `serializers.py`, and `urls.py`, as well as a `tests/` package. This keeps authentication, board, and task logic cleanly separated and independently testable.

## Contributing

Contributions are always welcome! If you have suggestions for improvements or want to propose changes, please open an issue. Alternatively, consider forking the repository and submitting a pull request.

## License

This project is licensed under the MIT License — © 2026 Simon Kiesner.
