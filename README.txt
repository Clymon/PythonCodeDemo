LEARNING LAB — AI Agent Coding with WorkBuddy and Python

An English LMS workshop project: My courses -> Course -> Chapter -> Lesson.
The prepared learner product supports ordinary reading, optional examples/resources/
checks and saved course progress. Its course data is fictional workshop material.
The AI-coding task is to improve the platform, not to study its sample syllabus.

STARTING PRODUCT
  git clone -b student https://github.com/Clymon/PythonCodeDemo.git learning-lab
  cd learning-lab
Start with docs/exercise-plan.txt and docs/agent-exploration.txt. Teachers bring a
lesson plan and two questions and want students to learn with them in this platform.
The Agent investigates; the human judges options, scope and a first usable slice.
The student branch intentionally has no teacher content-maintenance implementation.

RUN — same one-process setup (Python 3.10+)
  python -m venv .venv
  Windows: .venv\Scripts\Activate.ps1
  macOS/Linux: source .venv/bin/activate
  python -m pip install -r requirements-lock.txt
  python app.py
Open http://127.0.0.1:5050. If occupied use python app.py --port 5051.
No Node build, CDN, cloud database or AI API key is needed to run the product.

TEST
  python -m unittest discover -s tests -v
Optional: python -m coverage run --source=learning_lab -m unittest discover -s tests
          python -m coverage report -m
Python coverage measures backend execution, not browser interaction or acceptance.

ORIGINAL METHODS
16 original Matt Skill folders and complete resources are in .codebuddy/skills/.
Read docs/skills-installation.txt and docs/skills-at-a-glance.txt. Select a method
for a real problem. Discussion -> synthesis -> tickets is useful for nontrivial
work, not mandatory for every tiny change. implement owns checks/review/commit.
Keep Default Permissions. Inspect actual native loading, not only picker names.

INSTRUCTOR REFERENCE
main includes a local Teaching demo at /teach: edit existing lesson text, preview,
save and inspect the student result. This is a prepared reference, not a WorkBuddy
execution record or a complete teacher identity/ownership system. Its visibility
and scope are one deliberate example. See instructor/content-authoring/ on main.
The class chooses its own supported solution; don't copy this policy by default.

See docs/checkpoints.txt for current LMS tags and historical pre-LMS examples.
All historical WorkBuddy claims remain scoped to the actual earlier client/product.
