---
name: learning-lab-feature
description: Implement a learner-visible feature in the Learning Lab Flask application across the browser, API, learning rules and persistence, with evidence against the agreed behavior.
---

1. Read the requested behavior and the applicable policy in docs/learning-rules.txt.
   For wrong-answer review, read docs/review-spec.txt. Resolve missing product
   decisions with the instructor; inspect files for implementation facts.
2. Trace the current request from the browser through routes.py to quiz.py and
   db.py. Choose one complete interaction with an observable result, including
   persistence when needed. State its input, expected output and acceptance check.
3. Add a behavioral check, run it and confirm the failure concerns that behavior.
   Implement the smallest complete interaction while preserving existing rules.
4. Run the relevant checks, then python -m unittest discover -s tests -v.
   Open the actual browser page and exercise the changed interaction. For review,
   verify an incorrect answer, correction, unchanged original score and refresh.
5. Inspect git diff for scope. Report the observed result, tests and remaining
   gaps. Save decisions and next steps in docs/handoff.txt when handing off.

Keep learner records in ignored instance/. Python coverage is evidence about
executed backend code; browser behavior needs its own check. Installing and
invoking this portable sample in WorkBuddy must be verified in that client.
