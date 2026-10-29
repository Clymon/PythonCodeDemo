INSTRUCTOR TRIAL SNAPSHOT: see REHEARSAL.txt. Ticket 01 only; Ticket 02 is open.

LEARNING LAB — AI Agent Coding with WorkBuddy and Python

A working browser learning platform for practising AI-assisted development.
People decide purpose, rules, scope, task boundaries and acceptance. The agent
investigates implementation facts, proposes options, builds and checks the change.
The sample Python/Git/testing lessons inside the app are fictional product data.

CHOOSE YOUR ENTRY POINT
Learner starting product:
  git clone --branch student https://github.com/Clymon/PythonCodeDemo.git learning-lab
Instructor reference, including the completed review feature:
  git clone https://github.com/Clymon/PythonCodeDemo.git learning-lab-reference
Enter the cloned folder. Start with docs/exercise-plan.txt and docs/course-map.txt.

RUN (Python 3.10 or later)
  python -m venv .venv
  Windows PowerShell: .venv\Scripts\Activate.ps1
  macOS / Linux: source .venv/bin/activate
  python -m pip install -r requirements-lock.txt
  python app.py
Open http://127.0.0.1:5050 . Stop with Ctrl+C.
If 5050 is busy: python app.py --port 5051 and open that port.
On Windows, .venv\Scripts\python.exe can be used directly without activation.
A single Python process serves HTML/CSS/JavaScript, the JSON API and local SQLite.
The app needs no Node build, CDN, external font, cloud database or AI API key.

WORKSHOP MATERIALS
  docs/client-brief.txt       the open feature request
  docs/learning-rules.txt     existing behavior to preserve
  .codebuddy/skills/            unchanged Matt Skills, dependencies and MIT notice
  docs/agents/                per-repo issue-tracker and domain-doc configuration
  .scratch/                  spec and separate tickets created during the exercise
  worksheets/                optional human decision and acceptance notes
  docs/assessment.txt        observable human design and acceptance actions

Use grill-me for open choices, to-spec for synthesis, to-tickets for complete
slices and implement for approved work. implement calls tdd and code-review.
Use handoff when another collaborator/harness needs a portable record.
Original names and source are preserved; choose methods to fit the task.
Source version and attribution: .codebuddy/skills/UPSTREAM.json and .codebuddy/skills/LICENSE.
Original setup-matt-pocock-skills configures the repository once before class.
Current client evidence and limitations: docs/workbuddy-rehearsal.txt.
Instructor guidance, examples and verification reports are on main under instructor/.

TEST AND INSPECT EVIDENCE
  python -m unittest discover -s tests -v
Optional backend coverage:
  python -m coverage run --branch --source=learning_lab -m unittest discover -s tests
  python -m coverage report -m
Coverage measures executed Python, not browser behavior. Assess the examples in
your confirmed spec; a test count or coverage threshold is not a course outcome.

PROJECT FACTS (ask the agent to investigate when relevant)
  app.py                      server entry point
  learning_lab/templates/      page structure
  learning_lab/static/         browser behavior and appearance
  learning_lab/routes.py       request validation and JSON responses
  learning_lab/quiz.py         learning rules
  learning_lab/db.py           SQLite persistence
  learning_lab/data/           server-side sample lesson/question content
Details: docs/architecture.txt. Personally tracing every source file is optional.

PERSISTENCE
instance/ stores the database and local session key, ignored by Git. Progress
survives refresh/restart with the same browser cookie. Different browser profiles
are different anonymous learners. Clearing cookies loses access to that profile's
records. Reading completion and original quiz score are different measures.
Use simulated content only. This classroom app runs locally on 127.0.0.1.

CHECKPOINTS
student is the learner starting point; main is the instructor reference.
New workshop demonstration checkpoints are documented in docs/checkpoints.txt.
Older baseline/review-red/review-green/teaching-ready/web-starter tags remain
historical references. The old batch of failing tests is not the classroom TDD loop.
Save your work before switching; ignored instance/ data is not reset by a switch.
The distribution bundle preserves Git history; source ZIP exports do not.

REFERENCES
Original Python project informed by Matt Pocock's engineering workflow. The
TypeScript exercise source and paid course text were not copied.
https://www.aihero.dev/workshops/ai-coding-crash-course
https://github.com/mattpocock/skills
https://flask.palletsprojects.com/en/stable/tutorial/
