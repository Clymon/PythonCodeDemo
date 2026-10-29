import unittest
from tests import test_app
from learning_lab import create_app, quiz

class ReviewTests(unittest.TestCase):
    setUp = test_app.ClassroomTests.setUp
    tearDown = test_app.ClassroomTests.tearDown
    answer = test_app.ClassroomTests.answer

    def candidates(self):
        response = self.client.get("/api/review")
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def test_repeated_errors_are_unique_and_in_bank_order(self):
        self.answer("git-local", "A")
        self.answer("python-input", "B")
        self.answer("python-input", "B")
        result = self.candidates()
        self.assertEqual([q["id"] for q in result["questions"]], ["python-input", "git-local"])
        self.assertEqual(result["count"], 2)
        self.assertNotIn("answer", result["questions"][0])
        self.assertNotIn("explanation", result["questions"][0])

    def test_correct_review_removes_error_without_rewriting_score(self):
        self.answer(choice="B")
        self.assertEqual(self.candidates()["count"], 1)
        result = self.answer(choice="A", mode="review")
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.get_json()["correct"])
        self.assertEqual(result.get_json()["score"], {"correct": 0, "answered": 1})
        self.assertEqual(result.get_json()["review_count"], 0)
        self.assertEqual(self.candidates()["count"], 0)
