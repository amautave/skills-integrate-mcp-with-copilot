import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from src import app as activities_app


class ActivityPersistenceTests(unittest.TestCase):
    def test_signup_survives_reload_and_unregister_is_persisted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "activities.json"
            original_activities = activities_app.activities

            with patch.object(activities_app, "ACTIVITIES_FILE", data_file):
                activities_app.activities = activities_app.load_activities(data_file)
                try:
                    activities_app.signup_for_activity(
                        "Chess Club", "student@mergington.edu"
                    )
                    loaded_activities = activities_app.load_activities(data_file)
                    self.assertIn(
                        "student@mergington.edu",
                        loaded_activities["Chess Club"]["participants"],
                    )

                    with self.assertRaises(HTTPException):
                        activities_app.signup_for_activity(
                            "Chess Club", "student@mergington.edu"
                        )

                    activities_app.unregister_from_activity(
                        "Chess Club", "student@mergington.edu"
                    )
                    loaded_activities = activities_app.load_activities(data_file)
                    self.assertNotIn(
                        "student@mergington.edu",
                        loaded_activities["Chess Club"]["participants"],
                    )
                finally:
                    activities_app.activities = original_activities

    def test_missing_file_returns_independent_default_roster(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_file = Path(temporary_directory) / "activities.json"

            activities = activities_app.load_activities(data_file)
            activities["Chess Club"]["participants"].append("student@mergington.edu")

            self.assertNotIn(
                "student@mergington.edu",
                activities_app.DEFAULT_ACTIVITIES["Chess Club"]["participants"],
            )


if __name__ == "__main__":
    unittest.main()