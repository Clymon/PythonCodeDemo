"""SQLite storage for anonymous classroom practice; catalog content stays in JSON."""
import sqlite3
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS enrollments (
    learner TEXT NOT NULL,
    course_id TEXT NOT NULL,
    last_lesson_id TEXT,
    opened_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (learner, course_id)
);
CREATE TABLE IF NOT EXISTS saved_lessons (
    learner TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    PRIMARY KEY (learner, lesson_id)
);
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner TEXT NOT NULL,
    question_id TEXT NOT NULL,
    choice TEXT NOT NULL,
    correct INTEGER NOT NULL CHECK(correct IN (0, 1)),
    mode TEXT NOT NULL CHECK(mode IN ('quiz', 'review')),
    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS attempts_learner ON attempts(learner, id);
CREATE TABLE IF NOT EXISTS completed_lessons (
    learner TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    PRIMARY KEY (learner, lesson_id)
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        connection = get_db()
        connection.executescript(SCHEMA)
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(enrollments)")}
        if "opened_order" not in columns:
            connection.execute("ALTER TABLE enrollments ADD COLUMN opened_order INTEGER NOT NULL DEFAULT 0")
        # Databases from the original workshop already contain learning activity.
        # Backfill only courses with evidence, preserving every existing position.
        with connection:
            for course in app.config["CATALOG"]["courses"]:
                for chapter in course["chapters"]:
                    for lesson in chapter["lessons"]:
                        connection.execute(
                            "INSERT OR IGNORE INTO enrollments(learner, course_id) "
                            "SELECT learner, ? FROM completed_lessons WHERE lesson_id = ? "
                            "UNION SELECT learner, ? FROM saved_lessons WHERE lesson_id = ?",
                            (course["id"], lesson["id"], course["id"], lesson["id"]),
                        )
                        for question in lesson.get("questions", []):
                            connection.execute(
                                "INSERT OR IGNORE INTO enrollments(learner, course_id) "
                                "SELECT DISTINCT learner, ? FROM attempts WHERE question_id = ?",
                                (course["id"], question["id"]),
                            )


def history(learner):
    return [dict(row) for row in get_db().execute(
        "SELECT * FROM attempts WHERE learner = ? ORDER BY id", (learner,))]


def save_attempt(learner, attempt):
    connection = get_db()
    with connection:
        cursor = connection.execute(
            "INSERT INTO attempts(learner,question_id,choice,correct,mode) VALUES (?,?,?,?,?)",
            (learner, attempt["question_id"], attempt["choice"],
             int(attempt["correct"]), attempt["mode"]))
    return cursor.lastrowid


def completed(learner):
    return [row["lesson_id"] for row in get_db().execute(
        "SELECT lesson_id FROM completed_lessons WHERE learner = ?", (learner,))]


def set_completed(learner, lesson_id, value):
    connection = get_db()
    with connection:
        if value:
            connection.execute("INSERT OR IGNORE INTO completed_lessons VALUES (?,?)",
                               (learner, lesson_id))
        else:
            connection.execute("DELETE FROM completed_lessons WHERE learner=? AND lesson_id=?",
                               (learner, lesson_id))

def enrollment(learner, course_id):
    row = get_db().execute(
        "SELECT last_lesson_id, opened_order FROM enrollments WHERE learner=? AND course_id=?",
        (learner, course_id),
    ).fetchone()
    return dict(row) if row is not None else None


def enroll(learner, course_id):
    connection = get_db()
    with connection:
        connection.execute("INSERT OR IGNORE INTO enrollments(learner,course_id) VALUES (?,?)",
                           (learner, course_id))
    return enrollment(learner, course_id)


def record_open(learner, course_id, lesson_id):
    connection = get_db()
    with connection:
        changed = connection.execute(
            "UPDATE enrollments SET last_lesson_id=?, opened_order=("
            "SELECT COALESCE(MAX(opened_order),0)+1 FROM enrollments WHERE learner=?"
            ") WHERE learner=? AND course_id=?",
            (lesson_id, learner, learner, course_id),
        )
    return changed.rowcount == 1


def saved_lessons(learner):
    return {row["lesson_id"] for row in get_db().execute(
        "SELECT lesson_id FROM saved_lessons WHERE learner = ?", (learner,))}


def save_lesson(learner, lesson_id):
    connection = get_db()
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO saved_lessons(learner, lesson_id) VALUES (?, ?)",
            (learner, lesson_id))
