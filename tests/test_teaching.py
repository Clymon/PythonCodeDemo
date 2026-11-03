"""Public behavior checks for the prepared instructor reference, not starter tasks."""
import tempfile
import unittest
from pathlib import Path
from learning_lab import create_app


class TeachingReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = {"TESTING": True, "SECRET_KEY": "reference-test",
                       "DATABASE": str(Path(self.temp.name) / "reference.sqlite")}
        self.client = create_app(self.config).test_client()
        data = self.client.get("/api/courses").get_json()
        self.headers = {"X-CSRF-Token": data["csrf_token"]}
        self.url = "/api/teaching/lessons/activity-design"
        self.value = {"title": "A focused comparison activity", "objective": "Compare two examples.",
                      "paragraphs": ["Choose two contrasting examples.", "Ask learners to explain one difference."]}

    def tearDown(self):
        self.temp.cleanup()

    def current(self, client=None):
        data = (client or self.client).get("/api/courses/teaching-practice").get_json()
        return data["course"]["chapters"][0]["lessons"][0]

    def test_saved_text_is_visible_to_the_learner_with_stable_identity(self):
        self.client.post("/api/lessons/activity-design/complete", json={"completed": True}, headers=self.headers)
        response = self.client.post(self.url, json=self.value, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        lesson = self.current()
        self.assertEqual(lesson["id"], "activity-design")
        self.assertEqual(lesson["title"], self.value["title"])
        self.assertEqual(lesson["paragraphs"], self.value["paragraphs"])
        self.assertEqual(len(lesson["resources"]), 1)
        progress = self.client.get("/api/courses/teaching-practice").get_json()["progress"]
        self.assertEqual(progress["completed"], ["activity-design"])

    def test_edit_survives_a_new_server_instance(self):
        self.client.post(self.url, json=self.value, headers=self.headers)
        restarted = create_app(self.config).test_client()
        self.assertEqual(self.current(restarted)["title"], self.value["title"])

    def test_invalid_content_leaves_the_previous_lesson_unchanged(self):
        original = self.current()
        for patch in [{"title": ""}, {"paragraphs": []}, {"paragraphs": [""]},
                      {"objective": None}, {"paragraphs": "text"}, {"title": "x" * 161}]:
            with self.subTest(patch=patch):
                self.assertEqual(self.client.post(self.url, json={**self.value, **patch}, headers=self.headers).status_code, 400)
        self.assertEqual(self.current(), original)

    def test_text_edit_cannot_change_ids_or_quiz_rules(self):
        self.assertEqual(self.client.post(self.url, json={**self.value, "id": "new-id"}, headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post(self.url, json={**self.value, "questions": []}, headers=self.headers).status_code, 400)

    def test_shared_write_protection_and_unknown_lesson(self):
        self.assertEqual(self.client.post(self.url, json=self.value).status_code, 403)
        self.assertEqual(self.client.post(self.url, json=[], headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post("/api/teaching/lessons/missing", json=self.value, headers=self.headers).status_code, 404)
        self.assertEqual(self.client.get("/teach").status_code, 200)
