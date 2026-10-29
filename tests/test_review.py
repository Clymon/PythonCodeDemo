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
