import unittest

from fastapi.testclient import TestClient

from src.app import activities, app


class SignupTests(unittest.TestCase):
    def setUp(self):
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
