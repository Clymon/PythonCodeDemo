from pathlib import Path
import tempfile
import unittest

from instructor_demo import create_walkthrough_app


class InstructorWalkthroughTests(unittest.TestCase):
    def test_opt_in_profile_has_two_real_enrollments_and_a_resume_position(self):
        with tempfile.TemporaryDirectory() as directory:
            app = create_walkthrough_app(Path(directory) / "walkthrough.sqlite")
            instructor = app.test_client()
            fresh = app.test_client()
            self.assertEqual(fresh.get("/api/dashboard").json["courses"], [])
            instructor.get("/instructor")
            courses = instructor.get("/api/courses").json["courses"]
            self.assertEqual(len(courses), 4)
            self.assertEqual(sum(c["enrollment"] is not None for c in courses), 2)
            studying = next(c for c in courses if c["id"] == "teaching-practice")
            self.assertEqual(studying["entry_lesson"]["id"], "activity-design")
            self.assertEqual(studying["completed"], ["useful-feedback"])
            self.assertEqual(studying["score"], {"correct": 1, "answered": 1})
            self.assertEqual(instructor.get("/api/saved-lessons").json["lessons"], [])
            self.assertEqual(fresh.get("/api/dashboard").json["courses"], [])
