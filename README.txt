LEARNING LAB — a Python full-stack classroom project

A small, working learning platform: browse three lessons, read code examples,
answer six questions, see Python's feedback and track reading progress.
English interface. Original sample content. Anonymous simulated practice only.

GET THE STUDENT STARTER
  git clone --branch student https://github.com/Clymon/PythonCodeDemo.git learning-lab
  cd learning-lab
GitHub's default main branch contains the instructor reference implementation.
This student branch is the starting product for the classroom exercises.

QUICK START (Python 3.10 or later)
  python -m venv .venv
  Windows PowerShell: .venv\Scripts\Activate.ps1
  macOS / Linux: source .venv/bin/activate
  python -m pip install -r requirements.txt
  python app.py
Open http://127.0.0.1:5050 . Stop the server with Ctrl+C.
If port 5050 is busy: python app.py --port 5051
Windows can also use .venv\Scripts\python directly without activation.

One Python process serves the page, static assets and JSON API. No Node, CDN,
external font, cloud database, API key or AI service is required by the app.
WorkBuddy is the agent used to change this codebase; it is not the app runtime.

TEST
  python -m pip install -r requirements-dev.txt
  python -m unittest discover -s tests -v
Optional coverage:
  python -m coverage run --source=learning_lab -m unittest discover -s tests
  python -m coverage report -m
Python coverage measures executed backend lines, not browser behavior.

WHERE TO LOOK
  app.py                       start the local server
  learning_lab/templates/       page structure
  learning_lab/static/app.css   appearance and responsive layout
  learning_lab/static/app.js    browser interaction and fetch calls
  learning_lab/routes.py        HTTP validation and JSON responses
  learning_lab/quiz.py          scoring and answer rules
  learning_lab/db.py            SQLite reads and writes
  learning_lab/data/catalog.json lessons and question bank (server-side)
  tests/                       domain, API, isolation and restart checks

Try changing title in catalog.json, restart Python, then refresh the browser.
That is the first small visible change. Follow one question from the browser's
form to POST /api/answers, through quiz.py and db.py, and back to feedback.

PERSISTENCE
instance/ contains the local SQLite database and session signing key. Both are
ignored by Git. Refreshing or restarting Python retains progress if you keep
the same browser profile/cookie. A different browser profile is a new anonymous
learner. Clearing cookies loses access to that profile's records. This is not
an authenticated account system or a production learning management system.
Lesson completion is self-reported reading progress, separate from quiz score.
The first valid quiz answer per question sets its original score permanently.

SCOPE
For a local training computer, not public hosting. Sample questions, no student
names, accounts, payments, file uploads or multi-user administration. Keep the
server on 127.0.0.1. Application tests use temporary databases.

REFERENCE
Inspired by the teaching structure of Matt Pocock's AI Coding Crash Course:
start inside a working product, explore it, make a visible change, clarify a
feature, implement a small slice, inspect evidence, and hand off context.
Matt's downloaded TypeScript repository remains separate; its source code and
paid course text are not copied. This is an original Python teaching project.
Flask tutorial: https://flask.palletsprojects.com/en/stable/tutorial/
SQLite setup: https://flask.palletsprojects.com/en/stable/tutorial/database/

TEACHING CHECKPOINTS
This student branch is the working starting product. Wrong-answer review is the
feature to build. Start with docs/exercise-plan.txt and docs/client-brief.txt.
The portable development workflow lives under teaching-skills/. It is a sample
to import and verify in WorkBuddy, not an automatically installed Skill.

The bundle also includes main (instructor reference), review-red (ten expected
failing review checks) and review-green (working review implementation). Save
your work before creating or switching branches. Ignored instance/ data stays
when you switch. The full bundle preserves history; ZIP exports do not.

For repeatable classroom setup, requirements-lock.txt records the versions used
in the instructor trial; pip install -r requirements-lock.txt installs those.
