import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from learning_lab import create_app, db, rewards
from rewards_demo import demo_app


class RewardsTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.config = {"TESTING":True, "DATABASE":str(Path(directory.name)/"lab.sqlite"), "SECRET_KEY":"qa"}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.headers = {"X-CSRF-Token": self.client.get("/api/courses").get_json()["csrf_token"]}
        self.post("/api/courses/teaching-practice/enroll")
        with self.client.session_transaction() as learner:
            self.learner = learner["learner"]

    def post(self, url, **data):
        return self.client.post(url, json=data, headers=self.headers)

    def complete(self, value=True):
        return self.post("/api/lessons/useful-feedback/complete", completed=value)

    def balance(self, app=None):
        with (app or self.app).app_context():
            return rewards.wallet(self.learner)["balance"]

    def test_reward_once_even_after_undo_or_restart(self):
        self.assertEqual(self.complete().json["reward_balance"], 10)
        self.assertEqual(self.complete(False).json["reward_balance"], 10)
        self.assertEqual(self.complete().json["reward_balance"], 10)
        self.assertEqual(self.balance(create_app(self.config)), 10)

    def test_quiz_and_visit_alone_earn_nothing(self):
        self.post("/api/courses/teaching-practice/lessons/useful-feedback/open")
        self.post("/api/answers", question_id="feedback-action", choice="B")
        self.assertEqual(self.balance(), 0)

    def test_redeem_and_retry_after_refresh(self):
        url = "/api/rewards/first-steps/redeem"
        self.assertEqual(self.post(url).status_code, 409)
        self.complete()
        self.assertEqual(self.client.post(url, json={}).status_code, 403)
        self.assertEqual(self.post(url).json["balance"], 0)
        self.assertTrue(self.post(url).json["owned"])
        self.assertIn(b"In your collection", self.client.get("/rewards").data)
        self.assertNotIn(b"In your collection", self.app.test_client().get("/rewards").data)
        self.assertEqual(self.balance(create_app(self.config)), 0)

    def test_two_simultaneous_redemptions_charge_once(self):
        self.complete()
        cookie = self.client.get_cookie("session").value
        def redeem(_):
            with self.app.test_client() as client:
                client.set_cookie("session", cookie)
                return client.post("/api/rewards/first-steps/redeem", json={}, headers=self.headers).status_code
        with ThreadPoolExecutor(2) as pool:
            self.assertEqual(list(pool.map(redeem, range(2))), [200,200])
        self.assertEqual(self.balance(), 0)

    def test_prior_completions_receive_one_award_on_upgrade(self):
        with self.app.app_context():
            conn=db.get_db()
            with conn:
                conn.execute("INSERT INTO completed_lessons VALUES (?,?)",(self.learner,"useful-feedback"))
        self.assertEqual(self.balance(create_app(self.config)), 10)
        self.assertEqual(self.balance(create_app(self.config)), 10)

    def test_prepared_instructor_begins_ready_without_points(self):
        with tempfile.TemporaryDirectory() as directory:
            client = demo_app(directory).test_client()
            response = client.get("/instructor", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'id="reward-balance">0', response.data)
            self.assertIn(b"Redeem for 10 points", client.get("/rewards").data)
