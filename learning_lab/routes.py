"""HTTP boundary: validate requests, call learning rules, return safe JSON."""
import secrets
from flask import Blueprint, current_app, jsonify, render_template, request, session
from . import db, quiz

bp = Blueprint("classroom", __name__)


def identity():
    if "learner" not in session:
        session["learner"] = secrets.token_hex(16)
        session["csrf"] = secrets.token_hex(24)
    return session["learner"]


def catalog():
    return current_app.config["CATALOG"]


def questions():
    return [q for lesson in catalog()["lessons"] for q in lesson["questions"]]


@bp.before_request
def validate_write():
    identity()
    if request.method == "POST":
        if not request.is_json:
            return jsonify(error="Send a JSON request."), 415
        if not secrets.compare_digest(request.headers.get("X-CSRF-Token", ""), session["csrf"]):
            return jsonify(error="Refresh the page and try again."), 403
        if not isinstance(request.get_json(silent=True), dict):
            return jsonify(error="Send a JSON object."), 400


def progress():
    attempts = db.history(identity())
    return {"score": quiz.first_attempt_score(attempts),
            "completed": db.completed(identity()), "attempt_count": len(attempts),
            "review_remaining": len(quiz.review_question_ids(attempts))}


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/dashboard")
def dashboard():
    content = catalog()
    lessons = [{**{k: v for k, v in lesson.items() if k != "questions"},
                "questions": [quiz.public_question(q) for q in lesson["questions"]]}
               for lesson in content["lessons"]]
    return jsonify(title=content["title"], subtitle=content["subtitle"], lessons=lessons,
                   csrf_token=session["csrf"], **progress())


@bp.get("/api/review")
def review():
    remaining = set(quiz.review_question_ids(db.history(identity())))
    questions = [{**quiz.public_question(q), "lesson_id": lesson["id"]}
                 for lesson in catalog()["lessons"]
                 for q in lesson["questions"] if q["id"] in remaining]
    return jsonify(review_remaining=len(questions), questions=questions)


@bp.post("/api/answers")
def answer():
    payload = request.get_json()
    question = next((q for q in questions() if q["id"] == payload.get("question_id")), None)
    if question is None:
        return jsonify(error="Question not found."), 404
    mode = payload.get("mode", "quiz")
    if mode != "quiz":
        return jsonify(error="Unknown practice mode."), 400
    try:
        attempt = quiz.make_attempt(question, payload.get("choice"), mode)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    db.save_attempt(identity(), attempt)
    return jsonify(correct=attempt["correct"], choice=attempt["choice"],
                   explanation=question["explanation"], **progress())


@bp.post("/api/lessons/<lesson_id>/complete")
def complete_lesson(lesson_id):
    if not any(lesson["id"] == lesson_id for lesson in catalog()["lessons"]):
        return jsonify(error="Lesson not found."), 404
    value = request.get_json().get("completed")
    if not isinstance(value, bool):
        return jsonify(error="Completed must be true or false."), 400
    db.set_completed(identity(), lesson_id, value)
    return jsonify(**progress())
