"""Start a resettable, local rewards demonstration in an isolated browser identity."""
import argparse
from pathlib import Path
import secrets
import tempfile

from flask import redirect, session
from learning_lab import create_app

def demo_app(directory):
    app = create_app({"DATABASE": str(Path(directory) / "demo.sqlite"),
                      "SECRET_KEY": secrets.token_hex(32), "SESSION_COOKIE_NAME": "lab_rewards_demo"})
    course = "teaching-practice"
    @app.get("/instructor")
    def enter():
        session.clear()
        session.update(profile)
        return redirect(f"/courses/{course}/lessons/useful-feedback")

    client = app.test_client()
    token = client.get("/api/courses").get_json()["csrf_token"]
    joined = client.post(f"/api/courses/{course}/enroll", json={}, headers={"X-CSRF-Token": token})
    if joined.status_code != 200:
        raise RuntimeError("Could not enroll the demonstration learner.")
    with client.session_transaction() as signed_in:
        profile = dict(signed_in)

    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5052)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        print(f"Open http://127.0.0.1:{args.port}/instructor", flush=True)
        demo_app(directory).run(host="127.0.0.1", port=args.port)
