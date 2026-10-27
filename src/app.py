"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import os
from pathlib import Path
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

PARTICIPANTS_FILE = Path(__file__).with_name("participants.json")


def load_participants() -> None:
    if not PARTICIPANTS_FILE.exists():
        return

    saved_participants = json.loads(PARTICIPANTS_FILE.read_text(encoding="utf-8"))
    if not isinstance(saved_participants, dict):
        raise ValueError(f"Invalid participant data in {PARTICIPANTS_FILE}")

    for activity_name, participants in saved_participants.items():
        if activity_name not in activities or not isinstance(participants, list) or not all(
            isinstance(email, str) for email in participants
        ):
            raise ValueError(f"Invalid participant data in {PARTICIPANTS_FILE}")

    for activity_name, participants in saved_participants.items():
        activities[activity_name]["participants"][:] = participants


def save_participants(participants_by_activity: dict[str, list[str]]) -> None:
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=PARTICIPANTS_FILE.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(participants_by_activity, temporary_file, indent=2)
            temporary_file.write("\n")

        temporary_path.replace(PARTICIPANTS_FILE)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


load_participants()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up for this activity"
        )

    updated_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }
    updated_participants[activity_name].append(email)
    save_participants(updated_participants)
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
