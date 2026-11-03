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

    def test_empty_review_has_no_questions(self):
        self.assertEqual(self.candidates(), {"questions": [], "count": 0})

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

    def test_wrong_review_stays_once(self):
        self.answer(choice="B")
        result = self.answer(choice="C", mode="review")
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.get_json()["correct"])
        self.assertEqual(self.candidates()["count"], 1)

    def test_invalid_review_and_ineligible_review_do_not_write(self):
        self.assertEqual(self.answer(mode="review").status_code, 409)
        self.answer(choice="B")
        self.assertEqual(self.answer(choice="Z", mode="review").status_code, 400)
        self.answer(choice="A", mode="review")
        self.assertEqual(self.answer(choice="B", mode="review").status_code, 409)
        self.assertEqual(self.client.get("/api/dashboard").get_json()["attempt_count"], 2)

    def test_latest_quiz_answer_changes_membership_but_not_original_score(self):
        self.answer(choice="A")
        self.answer(choice="B")
        self.assertEqual(self.candidates()["count"], 1)
        self.assertEqual(self.client.get("/api/dashboard").get_json()["score"],
                         {"correct": 1, "answered": 1})
        self.answer(choice="A")
        self.assertEqual(self.candidates()["count"], 0)

    def test_review_is_isolated_between_profiles(self):
        self.answer(choice="B")
        other = self.app.test_client()
        other.get("/api/dashboard")
        result = other.get("/api/review")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()["count"], 0)

    def test_review_survives_new_server_instance(self):
        self.answer(choice="B")
        cookie = self.client.get_cookie("session")
        restarted = create_app(self.config).test_client()
        restarted.set_cookie("session", cookie.value)
        result = restarted.get("/api/review")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()["questions"][0]["id"], "python-input")


class ReviewRuleTests(unittest.TestCase):
    def test_latest_answer_wins_and_unanswered_questions_are_excluded(self):
        bank = [{"id": "q1"}, {"id": "q2"}, {"id": "q3"}]
        attempts = [{"question_id": "q1", "correct": False},
                    {"question_id": "q2", "correct": False},
                    {"question_id": "q1", "correct": True}]
        self.assertEqual(quiz.review_questions(attempts, bank), [{"id": "q2"}])

    def test_candidates_follow_bank_order(self):
        bank = [{"id": "q1"}, {"id": "q2"}]
        attempts = [{"question_id": "q2", "correct": False},
                    {"question_id": "q1", "correct": False},
                    {"question_id": "q2", "correct": False}]
        self.assertEqual(quiz.review_questions(attempts, bank), bank)


if __name__ == "__main__":
    unittest.main()
