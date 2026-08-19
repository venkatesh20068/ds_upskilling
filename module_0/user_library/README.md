# User Library API

A simple CRUD (Create, Read, Update, Delete) REST API built with **FastAPI** for managing user information.

## Features

- Create a new user
- Get all users
- Get a user by ID
- Update user details
- Delete a user
- Prevent duplicate email addresses

## Technologies

- Python 3
- FastAPI
- Uvicorn
- Pydantic

## Installation

1. Clone the repository.

```bash
git clone https://github.com/venkatesh20068/ds_upskilling.git
cd ds_upskilling\module-0\user_library
```

2. Install dependencies.

```bash
pip install fastapi uvicorn
```

## Run the Application

Start the server using:

```bash
python main.py
```

or

```bash
uvicorn main:app --reload
```

The application will start at:

```
http://127.0.0.1:8001
```

## API Documentation

Interactive Swagger documentation is available at:

```
http://127.0.0.1:8001/docs
```

ReDoc documentation is available at:

```
http://127.0.0.1:8001/redoc
```

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/users/` | Create a new user |
| GET | `/users/` | Get all users |
| GET | `/users/{user_id}` | Get a user by ID |
| PUT | `/users/{user_id}` | Update a user |
| DELETE | `/users/{user_id}` | Delete a user |

## User Object

```json
{
  "name": "John Doe",
  "dob": "1998-01-15",
  "gender": "Male",
  "city": "Chennai",
  "email": "john@example.com",
  "phone": "9876543210"
}
```

## Notes

- Data is stored in an in-memory list (`users_db`).
- All data will be lost when the application is stopped or restarted.
- Email addresses must be unique.

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Request successful |
| 201 | User created successfully |
| 404 | User not found |
| 409 | Email already exists |

## Project Structure

```
.
├── main.py
└── README.md
```

## Author

Your Name