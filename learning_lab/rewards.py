"""Learning rewards earned once per lesson and spent on personal badges."""
from flask import Blueprint, jsonify, render_template, session
from . import db
from .routes import identity

bp = Blueprint("rewards", __name__)
POINTS_PER_LESSON = 10
FIRST_STEPS = "first-steps"
BADGE_PRICE = 10

SCHEMA = """
CREATE TABLE IF NOT EXISTS lesson_awards (
    learner TEXT NOT NULL, lesson_id TEXT NOT NULL, points INTEGER NOT NULL,
    PRIMARY KEY (learner, lesson_id)
);
CREATE TABLE IF NOT EXISTS owned_badges (
    learner TEXT NOT NULL, badge TEXT NOT NULL, price INTEGER NOT NULL,
    PRIMARY KEY (learner, badge)
);
"""


def setup(app):
    with app.app_context():
        conn = db.get_db()
        conn.executescript(SCHEMA)
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO lesson_awards SELECT learner, lesson_id, ? FROM completed_lessons",
                (POINTS_PER_LESSON,),
            )
    app.register_blueprint(bp)


def award_completion(conn, learner, lesson_id):
    conn.execute("INSERT OR IGNORE INTO lesson_awards VALUES (?, ?, ?)",
                 (learner, lesson_id, POINTS_PER_LESSON))


def wallet(learner):
    conn = db.get_db()
    row = conn.execute("""
        SELECT COALESCE((SELECT SUM(points) FROM lesson_awards WHERE learner=?),0) AS earned,
               COALESCE((SELECT SUM(price) FROM owned_badges WHERE learner=?),0) AS spent,
               EXISTS(SELECT 1 FROM owned_badges WHERE learner=? AND badge=?) AS owned
    """, (learner, learner, learner, FIRST_STEPS)).fetchone()
    return dict(balance=row["earned"] - row["spent"], earned=row["earned"], spent=row["spent"],
                owned=bool(row["owned"]), price=BADGE_PRICE)


@bp.get("/rewards")
def rewards_page():
    return render_template("rewards.html", wallet=wallet(identity()), token=session["csrf"])


@bp.post("/api/rewards/first-steps/redeem")
def redeem():
    learner = identity()
    conn = db.get_db()
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        current = wallet(learner)
        if current["owned"]:
            return jsonify(current)
        if current["balance"] < BADGE_PRICE:
            return jsonify(error="Earn 10 points to get First Steps."), 409
        conn.execute("INSERT INTO owned_badges VALUES (?, ?, ?)", (learner, FIRST_STEPS, BADGE_PRICE))
        return jsonify(wallet(learner))
