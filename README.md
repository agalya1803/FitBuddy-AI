# FitBuddy - AI Fitness Plan Generator

FitBuddy is a web-based AI fitness application built using FastAPI, Jinja2, SQLite, SQLAlchemy and Google's Gemini AI.

## Features

- User fitness details
- AI-generated 7-day workout plan
- Nutrition and recovery tip
- Feedback-based workout plan update
- SQLite database
- SQLAlchemy ORM
- View all users
- Delete user
- REST API
- Swagger API documentation
- Responsive web interface
- Gemini AI integration

## Project Structure

```text
FitBuddy/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── routes.py
│   │
│   └── ai/
│       ├── __init__.py
│       ├── gemini_client.py
│       ├── gemini_generator.py
│       ├── gemini_flash_generator.py
│       └── updated_plan.py
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
│
├── static/
│   └── style.css
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md