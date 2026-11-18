import sqlite3
import tempfile
import unittest
from pathlib import Path

from learning_lab import create_app


class EnrollmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = Path(self.tmp.name) / "learning.sqlite"
        self.config = {"TESTING": True, "SECRET_KEY": "stable-test-key", "DATABASE": str(self.db_path)}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.headers = {"X-CSRF-Token": self.client.get("/api/dashboard").json["csrf_token"]}

    def enroll(self, course):
        return self.client.post(f"/api/courses/{course}/enroll", json={}, headers=self.headers)

    def open(self, course, lesson):
        return self.client.post(f"/api/courses/{course}/lessons/{lesson}/open", json={}, headers=self.headers)

    def test_fresh_profile_can_browse_but_has_no_enrolled_courses(self):
        self.assertEqual(self.client.get("/api/dashboard").json["courses"], [])
        catalog = self.client.get("/api/courses").json["courses"]
        self.assertEqual(len(catalog), 4)
        for course in catalog:
            self.assertIsNone(course["enrollment"])
            self.assertGreater(course["duration_minutes"], 0)
        detail = self.client.get("/api/courses/useful-feedback").json
        lesson = detail["course"]["chapters"][0]["lessons"][0]
        self.assertIn("title", lesson)
        self.assertNotIn("paragraphs", lesson)
        self.assertFalse(self.client.get("/api/dashboard").json["lessons"])
        redirect = self.client.get("/courses/useful-feedback/lessons/notice-the-work")
        self.assertTrue(redirect.location.endswith("/courses/useful-feedback"))

    def test_writes_require_enrollment_and_validate_lesson_ownership(self):
        self.assertEqual(self.open("useful-feedback", "notice-the-work").status_code, 403)
        self.assertEqual(self.enroll("missing").status_code, 404)
        self.assertEqual(self.client.post("/api/answers", json={"question_id":"python-input", "choice":"A"},
                                         headers=self.headers).status_code, 403)
        self.assertEqual(self.client.post("/api/lessons/first-program/complete", json={"completed":True},
                                         headers=self.headers).status_code, 403)
        self.enroll("useful-feedback")
        self.assertEqual(self.open("useful-feedback", "activity-design").status_code, 404)
        self.assertEqual(self.open("useful-feedback", "notice-the-work").status_code, 200)
        detail = self.client.get("/api/courses/useful-feedback").json
        self.assertTrue(detail["course"]["chapters"][0]["lessons"][0]["paragraphs"])

    def test_resume_is_independent_per_course_and_latest_across_courses(self):
        self.enroll("ai-coding")
        self.enroll("useful-feedback")
        self.open("ai-coding", "first-program")
        self.open("useful-feedback", "choose-one-revision")
        self.open("ai-coding", "git-checkpoint")
        self.enroll("useful-feedback")
        other = self.app.test_client()
        self.assertFalse(other.get("/api/dashboard").json["courses"])
        fresh = create_app(self.config).test_client()
        fresh.set_cookie("session", self.client.get_cookie("session").value)
        courses = fresh.get("/api/dashboard").json["courses"]
        self.assertEqual(len(courses), 2)
        latest = max(courses, key=lambda c: c["enrollment"]["opened_order"])
        self.assertEqual((latest["id"], latest["entry_lesson"]["id"]), ("ai-coding","git-checkpoint"))
        self.assertEqual(fresh.get("/api/courses/useful-feedback").json["entry_lesson"]["id"], "choose-one-revision")
        self.assertEqual(latest["completed"], [])
        self.assertEqual(latest["attempt_count"], 0)

    def test_old_records_restore_only_courses_with_real_activity(self):
        with self.client.session_transaction() as sess:
            learner = sess["learner"]
        with sqlite3.connect(self.db_path) as db:
            db.execute("DROP TABLE enrollments")
            db.execute("INSERT INTO completed_lessons VALUES (?,?)", (learner,"activity-design"))
            db.execute("INSERT INTO attempts(learner,question_id,choice,correct,mode) VALUES (?,?,?,?,?)",
                       (learner, "python-input", "A", 1, "quiz"))
        restarted = create_app(self.config).test_client()
        restarted.set_cookie("session", self.client.get_cookie("session").value)
        dashboard = restarted.get("/api/dashboard").json
        self.assertEqual([c["id"] for c in dashboard["courses"]], ["ai-coding","teaching-practice"])
        self.assertEqual(dashboard["score"], {"correct":1,"answered":1})
        self.assertEqual(dashboard["completed"], ["activity-design"])
        self.assertEqual(dashboard["attempt_count"], 1)
