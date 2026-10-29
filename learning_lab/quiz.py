"""Learning rules, independent of Flask, HTML and SQLite."""


def make_attempt(question, choice, mode="quiz"):
    if mode not in ("quiz", "review"):
        raise ValueError("Unknown practice mode.")
    if not isinstance(choice, str) or choice.strip().upper() not in question["options"]:
        raise ValueError("Choose one of: " + ", ".join(question["options"]))
    choice = choice.strip().upper()
    return {"question_id": question["id"], "choice": choice,
            "correct": choice == question["answer"], "mode": mode}


def first_attempt_score(attempts):
    first = {}
    for attempt in attempts:
        if attempt["mode"] == "quiz":
            first.setdefault(attempt["question_id"], bool(attempt["correct"]))
    return {"correct": sum(first.values()), "answered": len(first)}


def public_question(question):
    return {key: question[key] for key in ("id", "prompt", "options")}
