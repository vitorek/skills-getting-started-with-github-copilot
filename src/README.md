# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- View the participant list and current availability for each activity
- Sign up for activities
- Prevent duplicate sign-ups for the same activity
- Refresh participant lists and availability after each successful sign-up
- Save participant emails to `participants.json` so they persist after an app restart

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity; duplicate sign-ups are rejected             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activity details are defined in the application, while participant emails are saved in
`participants.json` alongside `app.py`. The file is created on the first successful
sign-up and loaded when the application starts. Keep this file to preserve sign-ups
between restarts; it is excluded from source control because it contains student email
addresses.
