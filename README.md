# Payroll System

A Django-based payroll management system.

## Features
- Employee Management
- Attendance Tracking (including ESSL integration)
- Salary Calculation
- Deduction Management

## Setup
1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install dependencies: `pip install -r requirements.txt` (Note: ensure requirements.txt is generated).
4. Create a `.env` file with `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`.
5. Run migrations: `python manage.py migrate`.
6. Run the server: `python manage.py runserver`.
