"""SQLite storage for anonymous classroom practice; catalog content stays in JSON."""
import sqlite3
from flask import current_app, g

SCHEMA = """
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
        get_db().executescript(SCHEMA)


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
