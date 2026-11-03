"""Prepared local instructor reference: edit existing lesson text, visible on save."""
import json
from flask import Blueprint, jsonify, render_template, request, g
from . import catalog, db

bp = Blueprint("teaching", __name__)


def init_app(app):
    with app.app_context():
        db.get_db().execute("""CREATE TABLE IF NOT EXISTS lesson_edits (
            lesson_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
            updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        db.get_db().commit()
    app.register_blueprint(bp)


@bp.get("/teach")
def workspace():
    return render_template("teaching.html")


@bp.post("/api/teaching/lessons/<lesson_id>")
def save_lesson(lesson_id):
    if catalog.lesson(lesson_id) is None:
        return jsonify(error="Lesson not found."), 404
    value = request.get_json()
    if set(value) != {"title", "objective", "paragraphs"}:
        return jsonify(error="Send title, objective and lesson paragraphs only."), 400
    title, objective, paragraphs = value["title"], value["objective"], value["paragraphs"]
    if not isinstance(title, str) or not title.strip() or len(title) > 160:
        return jsonify(error="Use a lesson title of 1 to 160 characters."), 400
    if not isinstance(objective, str) or len(objective) > 1000:
        return jsonify(error="Keep the learning objective within 1,000 characters."), 400
    if (not isinstance(paragraphs, list) or not 1 <= len(paragraphs) <= 30
            or not all(isinstance(p, str) and p.strip() for p in paragraphs)
            or sum(map(len, paragraphs)) > 20000):
        return jsonify(error="Add 1 to 30 non-empty paragraphs, within 20,000 characters."), 400
    payload = {"title": title.strip(), "objective": objective.strip(),
               "paragraphs": [p.strip() for p in paragraphs]}
    connection = db.get_db()
    with connection:
        connection.execute("""INSERT INTO lesson_edits(lesson_id,payload) VALUES (?,?)
            ON CONFLICT(lesson_id) DO UPDATE SET payload=excluded.payload, updated=CURRENT_TIMESTAMP""",
            (lesson_id, json.dumps(payload)))
    g.pop("catalog_snapshot", None)
    return jsonify(saved=True, lesson={k: catalog.lesson(lesson_id)[k] for k in payload},
                   message="Saved. Learners can see the updated lesson.")
