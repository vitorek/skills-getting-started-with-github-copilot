import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.app import activities, app, load_participants


class SignupTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.participants_file = Path(self.temp_dir.name) / "participants.json"
        self.participants_file_patch = patch(
            "src.app.PARTICIPANTS_FILE",
            self.participants_file,
        )
        self.participants_file_patch.start()
        self.addCleanup(self.participants_file_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

        self.client = TestClient(app)
        self.original_participants = {
            name: list(activity["participants"])
            for name, activity in activities.items()
        }

    def tearDown(self):
        for name, participants in self.original_participants.items():
            activities[name]["participants"][:] = participants

    def test_duplicate_signup_for_same_activity_is_rejected(self):
        email = "duplicate-check@mergington.edu"
        signup_url = "/activities/Chess%20Club/signup"

        first_response = self.client.post(signup_url, params={"email": email})
        duplicate_response = self.client.post(signup_url, params={"email": email})

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(
            duplicate_response.json()["detail"],
            "Student is already signed up for this activity",
        )
        self.assertEqual(
            activities["Chess Club"]["participants"].count(email),
            1,
        )

    def test_student_can_sign_up_for_a_different_activity(self):
        email = "multiple-activities@mergington.edu"

        chess_response = self.client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )
        programming_response = self.client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email},
        )

        self.assertEqual(chess_response.status_code, 200)
        self.assertEqual(programming_response.status_code, 200)

    def test_signup_is_restored_from_file(self):
        email = "persistent-check@mergington.edu"
        response = self.client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.participants_file.exists())

        activities["Chess Club"]["participants"].remove(email)
        load_participants()

        self.assertIn(email, activities["Chess Club"]["participants"])
