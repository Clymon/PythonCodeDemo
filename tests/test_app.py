import json
import tempfile
import unittest
from pathlib import Path
from learning_lab import create_app, quiz


class ClassroomTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = {"TESTING": True, "SECRET_KEY": "classroom-test-only",
                       "DATABASE": str(Path(self.directory.name) / "test.sqlite")}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.initial = self.client.get("/api/dashboard").get_json()
        self.headers = {"X-CSRF-Token": self.initial["csrf_token"]}

    def tearDown(self):
        self.directory.cleanup()

    def answer(self, question_id="python-input", choice="A", mode="quiz"):
        return self.client.post("/api/answers", json={"question_id": question_id,
            "choice": choice, "mode": mode}, headers=self.headers)

    def test_real_page_and_local_assets_are_served(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html lang="en">', response.data)
        for name in ("app.js", "app.css", "mark.svg"):
            with self.client.get("/static/" + name) as asset:
                self.assertEqual(asset.status_code, 200)

    def test_fresh_profile_has_lessons_without_answer_keys(self):
        self.assertEqual(len(self.initial["lessons"]), 3)
        self.assertEqual(self.initial["score"], {"correct": 0, "answered": 0})
        self.assertEqual(self.initial["completed"], [])
        for lesson in self.initial["lessons"]:
            for question in lesson["questions"]:
                self.assertEqual(set(question), {"id", "prompt", "options"})

    def test_answer_is_checked_by_python_and_saved(self):
        response = self.answer(choice=" a ")
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result["correct"])
        self.assertEqual(result["choice"], "A")
        self.assertIn("argument", result["explanation"])
        self.assertEqual(result["score"], {"correct": 1, "answered": 1})
        self.assertEqual(result["attempt_count"], 1)

    def test_repeating_a_question_does_not_rewrite_first_score(self):
        self.answer(choice="B")
        result = self.answer(choice="A").get_json()
        self.assertTrue(result["correct"])
        self.assertEqual(result["score"], {"correct": 0, "answered": 1})
        self.assertEqual(result["attempt_count"], 2)

    def test_invalid_options_and_non_string_choices_do_not_write(self):
        for choice in ("Z", "", None, 1, ["A"]):
            with self.subTest(choice=choice):
                self.assertEqual(self.answer(choice=choice).status_code, 400)
        self.assertEqual(self.client.get("/api/dashboard").get_json()["attempt_count"], 0)

    def test_unknown_question_and_mode_do_not_write(self):
        self.assertEqual(self.answer(question_id="missing").status_code, 404)
        self.assertEqual(self.answer(mode="unknown").status_code, 400)
        self.assertEqual(self.client.get("/api/dashboard").get_json()["attempt_count"], 0)

    def test_writes_require_json_object_and_browser_token(self):
        self.assertEqual(self.client.post("/api/answers", data="text").status_code, 415)
        self.assertEqual(self.client.post("/api/answers", json={}).status_code, 403)
        self.assertEqual(self.client.post("/api/answers", data="{", content_type="application/json",
                         headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post("/api/answers", json=[], headers=self.headers).status_code, 400)

    def test_completing_lesson_is_independent_of_quiz_score(self):
        url = "/api/lessons/first-program/complete"
        for _ in range(2):
            result = self.client.post(url, json={"completed": True}, headers=self.headers).get_json()
            self.assertEqual(result["completed"], ["first-program"])
            self.assertEqual(result["score"]["answered"], 0)
        result = self.client.post(url, json={"completed": False}, headers=self.headers).get_json()
        self.assertEqual(result["completed"], [])

    def test_invalid_lesson_completion_is_rejected(self):
        self.assertEqual(self.client.post("/api/lessons/no-such-lesson/complete",
            json={"completed": True}, headers=self.headers).status_code, 404)
        self.assertEqual(self.client.post("/api/lessons/first-program/complete",
            json={"completed": "true"}, headers=self.headers).status_code, 400)

    def test_two_browser_profiles_are_isolated(self):
        self.answer()
        second = self.app.test_client()
        result = second.get("/api/dashboard").get_json()
        self.assertEqual(result["attempt_count"], 0)
        self.assertEqual(result["score"]["answered"], 0)

    def test_new_server_instance_reads_saved_sqlite_progress(self):
        self.answer()
        self.client.post("/api/lessons/first-program/complete", json={"completed": True},
                         headers=self.headers)
        cookie = self.client.get_cookie("session")
        restarted = create_app(self.config).test_client()
        restarted.set_cookie("session", cookie.value)
        result = restarted.get("/api/dashboard").get_json()
        self.assertEqual(result["attempt_count"], 1)
        self.assertEqual(result["completed"], ["first-program"])


class LearningRuleTests(unittest.TestCase):
    def test_review_attempts_do_not_contribute_to_first_quiz_score(self):
        score = quiz.first_attempt_score([{"question_id": "q1", "correct": True, "mode": "review"}])
        self.assertEqual(score, {"correct": 0, "answered": 0})

    def test_unknown_domain_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            quiz.make_attempt({"id": "q1", "options": {"A": "Yes"}, "answer": "A"}, "A", "other")


if __name__ == "__main__":
    unittest.main()
