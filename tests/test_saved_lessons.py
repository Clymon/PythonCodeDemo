from pathlib import Path
import tempfile
import unittest

from learning_lab import create_app


class SavedLessonTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.config = {"TESTING": True, "SECRET_KEY": "test-browser-profile",
                       "DATABASE": str(Path(directory.name) / "test.sqlite")}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.headers = {"X-CSRF-Token": self.client.get("/api/courses").json["csrf_token"]}
        self.save_path = "/api/lessons/first-program/save"

    def test_saving_and_reopening_an_already_completed_lesson(self):
        self.client.post("/api/lessons/first-program/complete",
                         json={"completed": True}, headers=self.headers)
        self.client.post("/api/answers", json={"question_id": "python-input", "choice": "A"},
                         headers=self.headers)
        course_url = "/api/courses/ai-coding"
        before = self.client.get(course_url).json["progress"]
        for _ in range(2):
            self.assertEqual(self.client.post(self.save_path, json={}, headers=self.headers).status_code, 200)
        item, = self.client.get("/api/saved-lessons").json["lessons"]
        self.assertEqual(item["id"], "first-program")
        self.assertEqual(self.client.get(f'/courses/{item["course_id"]}/lessons/{item["id"]}').status_code, 200)
        after = self.client.get(course_url).json
        self.assertEqual(after["progress"], before)
        self.assertEqual(after["saved_lesson_ids"], ["first-program"])
        self.assertEqual(self.client.get("/api/courses/teaching-practice").json["saved_lesson_ids"], [])

    def test_bookmarks_survive_restart_and_belong_to_one_profile(self):
        self.client.post(self.save_path, json={}, headers=self.headers)
        fresh = create_app(self.config).test_client()
        self.assertEqual(fresh.get("/api/saved-lessons").json["lessons"], [])
        fresh.set_cookie("session", self.client.get_cookie("session").value)
        self.assertEqual([l["id"] for l in fresh.get("/api/saved-lessons").json["lessons"]],
                         ["first-program"])

    def test_unknown_lesson_and_missing_token_do_not_add_bookmarks(self):
        self.assertEqual(self.client.post("/api/lessons/missing/save", json={},
                                          headers=self.headers).status_code, 404)
        self.assertEqual(self.client.post(self.save_path, json={}).status_code, 403)
        self.assertEqual(self.client.get("/api/saved-lessons").json["lessons"], [])
