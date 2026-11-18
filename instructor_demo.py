"""Run an isolated instructor walkthrough using real course and learner actions."""
import argparse
from pathlib import Path
import secrets
import tempfile

from flask import redirect, session
from learning_lab import create_app


def create_walkthrough_app(database):
    app = create_app({
        "DATABASE": str(database),
        "SECRET_KEY": secrets.token_hex(32),
        "SESSION_COOKIE_NAME": "learning_lab_instructor",
    })
    client = app.test_client()
    token = client.get("/api/courses").get_json()["csrf_token"]
    actions = [
        ("/api/courses/teaching-practice/enroll", {}),
        ("/api/courses/ai-coding/enroll", {}),
        ("/api/courses/teaching-practice/lessons/useful-feedback/open", {}),
        ("/api/answers", {"question_id": "feedback-action", "choice": "B"}),
        ("/api/lessons/useful-feedback/complete", {"completed": True}),
        ("/api/courses/teaching-practice/lessons/activity-design/open", {}),
    ]
    for path, payload in actions:
        response = client.post(path, json=payload, headers={"X-CSRF-Token": token})
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f"Walkthrough setup failed at {path}: {response.status_code}")

    with client.session_transaction() as learner:
        instructor_session = dict(learner)

    @app.get("/instructor")
    def enter_walkthrough():
        session.clear()
        session.update(instructor_session)
        return redirect("/")

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the prepared instructor profile.")
    parser.add_argument("--port", type=int, default=5051)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="learning-lab-instructor-") as directory:
        application = create_walkthrough_app(Path(directory) / "walkthrough.sqlite")
        print(f"Open the prepared instructor profile at http://127.0.0.1:{args.port}/instructor", flush=True)
        application.run(host="127.0.0.1", port=args.port)
