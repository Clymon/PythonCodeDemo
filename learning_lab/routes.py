"""HTTP interface for course navigation, practice and saved learning progress."""
import secrets
from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from . import catalog, db, quiz

bp = Blueprint("classroom", __name__)


def identity():
    if "learner" not in session:
        session["learner"] = secrets.token_hex(16)
        session["csrf"] = secrets.token_hex(24)
    if not session.permanent:
        session.permanent = True
    return session["learner"]


@bp.before_app_request
def validate_write():
    identity()
    if request.method == "POST":
        if not request.is_json:
            return jsonify(error="Send a JSON request."), 415
        if not secrets.compare_digest(request.headers.get("X-CSRF-Token", ""), session["csrf"]):
            return jsonify(error="Refresh the page and try again."), 403
        if not isinstance(request.get_json(silent=True), dict):
            return jsonify(error="Send a JSON object."), 400


def progress(selected=None):
    visible_lessons = catalog.lessons(selected)
    lesson_ids = {l["id"] for l in visible_lessons}
    question_ids = {q["id"] for l in visible_lessons for q in l.get("questions", [])}
    attempts = [a for a in db.history(identity()) if a["question_id"] in question_ids]
    completed = [key for key in db.completed(identity()) if key in lesson_ids]
    return {"score": quiz.first_attempt_score(attempts), "completed": completed,
            "attempt_count": len(attempts), "lesson_count": len(visible_lessons),
            "question_count": len(question_ids),
            "completion_percent": round(100 * len(completed) / len(visible_lessons)) if visible_lessons else 0}


def summary(selected):
    enrollment = db.enrollment(identity(), selected["id"])
    learning = progress(selected)
    lessons = catalog.lessons(selected)
    by_id = {lesson["id"]: lesson for lesson in lessons}
    last = by_id.get(enrollment["last_lesson_id"]) if enrollment else None
    entry = last or next((lesson for lesson in lessons if lesson["id"] not in learning["completed"]),
                         lessons[0] if lessons else None)
    return {**{k: v for k, v in selected.items() if k != "chapters"},
            "chapter_count": len(selected.get("chapters", [])),
            "duration_minutes": sum(lesson.get("minutes", 0) for lesson in lessons), **learning, "enrollment": enrollment,
            "entry_lesson": {"id": entry["id"], "title": entry["title"]} if entry else None}


def enrollment_required():
    return jsonify(error="Enroll in this course to start learning."), 403


@bp.get("/")
@bp.get("/catalog")
@bp.get("/courses/<course_id>")
@bp.get("/courses/<course_id>/lessons/<lesson_id>")
def index(course_id=None, lesson_id=None):
    if course_id:
        selected = catalog.course(course_id)
        if selected is None or (lesson_id and lesson_id not in {l["id"] for l in catalog.lessons(selected)}):
            return render_template("not-found.html"), 404
        if lesson_id and db.enrollment(identity(), course_id) is None:
            return redirect(url_for(".index", course_id=course_id))
    return render_template("index.html")


@bp.get("/api/courses")
def course_list():
    return jsonify(title=catalog.content()["title"], courses=[summary(c) for c in catalog.courses()],
                   csrf_token=session["csrf"])


@bp.get("/api/courses/<course_id>")
def course_detail(course_id):
    selected = catalog.course(course_id)
    if selected is None:
        return jsonify(error="Course not found."), 404
    summary_data = summary(selected)
    course = catalog.public_course(selected)
    if summary_data["enrollment"] is None:
        for chapter in course["chapters"]:
            chapter["lessons"] = [{key: lesson[key] for key in ("id","title","minutes") if key in lesson}
                                  for lesson in chapter["lessons"]]
    return jsonify(course=course, progress=progress(selected), enrollment=summary_data["enrollment"],
                   entry_lesson=summary_data["entry_lesson"], csrf_token=session["csrf"])


@bp.post("/api/courses/<course_id>/enroll")
def join_course(course_id):
    if catalog.course(course_id) is None:
        return jsonify(error="Course not found."), 404
    return jsonify(enrollment=db.enroll(identity(), course_id))


@bp.post("/api/courses/<course_id>/lessons/<lesson_id>/open")
def open_lesson(course_id, lesson_id):
    selected = catalog.course(course_id)
    if selected is None or lesson_id not in {item["id"] for item in catalog.lessons(selected)}:
        return jsonify(error="Lesson not found in this course."), 404
    if not db.record_open(identity(), course_id, lesson_id):
        return enrollment_required()
    return jsonify(last_lesson_id=lesson_id)


@bp.get("/api/dashboard")
def dashboard():
    courses = [c for c in catalog.courses() if db.enrollment(identity(), c["id"]) is not None]
    summaries = [summary(c) for c in courses]
    lessons = [lesson for c in courses for chapter in catalog.public_course(c)["chapters"]
               for lesson in chapter["lessons"]]
    completed = [lid for c in summaries for lid in c["completed"]]
    return jsonify(title=catalog.content()["title"], courses=summaries, lessons=lessons,
                   completed=completed, lesson_count=len(lessons),
                   completion_percent=round(100 * len(completed) / len(lessons)) if lessons else 0,
                   score={key: sum(c["score"][key] for c in summaries) for key in ("correct", "answered")},
                   attempt_count=sum(c["attempt_count"] for c in summaries),
                   question_count=sum(c["question_count"] for c in summaries), csrf_token=session["csrf"])


@bp.post("/api/answers")
def answer():
    payload = request.get_json()
    question = next((q for q in catalog.questions() if q["id"] == payload.get("question_id")), None)
    if question is None:
        return jsonify(error="Question not found."), 404
    if payload.get("mode", "quiz") != "quiz":
        return jsonify(error="Unknown practice mode."), 400
    try:
        attempt = quiz.make_attempt(question, payload.get("choice"), "quiz")
    except ValueError as error:
        return jsonify(error=str(error)), 400
    owner = next(c for c in catalog.courses() if question in catalog.questions(c))
    if db.enrollment(identity(), owner["id"]) is None:
        return enrollment_required()
    db.save_attempt(identity(), attempt)
    return jsonify(correct=attempt["correct"], choice=attempt["choice"],
                   explanation=question["explanation"], **progress())


@bp.post("/api/lessons/<lesson_id>/complete")
def complete_lesson(lesson_id):
    if catalog.lesson(lesson_id) is None:
        return jsonify(error="Lesson not found."), 404
    value = request.get_json().get("completed")
    if not isinstance(value, bool):
        return jsonify(error="Completed must be true or false."), 400
    owner = next(c for c in catalog.courses() if any(l["id"] == lesson_id for l in catalog.lessons(c)))
    if db.enrollment(identity(), owner["id"]) is None:
        return enrollment_required()
    db.set_completed(identity(), lesson_id, value)
    return jsonify(**progress())
