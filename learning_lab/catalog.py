"""Course reading interface: prepared content with saved local text overrides."""
import copy
import json
from pathlib import Path
from flask import current_app, g
from . import quiz, db


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    seen = {"course": set(), "chapter": set(), "lesson": set(), "question": set()}
    def unique(kind, item):
        key = item.get("id")
        if not isinstance(key, str) or not key or key in seen[kind]:
            raise ValueError(f"Every {kind} needs a unique, stable id.")
        seen[kind].add(key)
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError(f"Every {kind} needs a title.")
    if not isinstance(data.get("courses"), list):
        raise ValueError("The catalog needs a courses list.")
    for course in data["courses"]:
        unique("course", course)
        for chapter in course.get("chapters", []):
            unique("chapter", chapter)
            for lesson in chapter.get("lessons", []):
                unique("lesson", lesson)
                if not isinstance(lesson.get("paragraphs"), list) or not all(isinstance(p, str) for p in lesson["paragraphs"]):
                    raise ValueError("Lesson paragraphs must be a list of text.")
                for question in lesson.get("questions", []):
                    key = question.get("id")
                    if not isinstance(key, str) or not key or key in seen["question"]:
                        raise ValueError("Every question needs a unique, stable id.")
                    seen["question"].add(key)
                    if question.get("answer") not in question.get("options", {}):
                        raise ValueError("The answer must be one of the question options.")
    return data


def content():
    if "catalog_snapshot" not in g:
        snapshot = copy.deepcopy(current_app.config["CATALOG"])
        edits = {row["lesson_id"]: json.loads(row["payload"])
                 for row in db.get_db().execute("SELECT lesson_id,payload FROM lesson_edits")}
        for course in snapshot["courses"]:
            for chapter in course.get("chapters", []):
                for lesson in chapter.get("lessons", []):
                    lesson.update(edits.get(lesson["id"], {}))
        g.catalog_snapshot = snapshot
    return g.catalog_snapshot


def courses():
    return content()["courses"]


def course(course_id):
    return next((c for c in courses() if c["id"] == course_id), None)


def lessons(selected=None):
    return [lesson for c in ([selected] if selected else courses())
            for chapter in c.get("chapters", []) for lesson in chapter.get("lessons", [])]


def lesson(lesson_id):
    return next((item for item in lessons() if item["id"] == lesson_id), None)


def questions(selected=None):
    return [q for l in lessons(selected) for q in l.get("questions", [])]


def public_course(selected):
    result = copy.deepcopy(selected)
    for chapter in result.get("chapters", []):
        for item in chapter.get("lessons", []):
            item["questions"] = [quiz.public_question(q) for q in item.get("questions", [])]
    return result
