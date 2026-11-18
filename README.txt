LEARNING LAB — AI Agent Coding with WorkBuddy and Python

Learning Lab is a small English-language learning platform. Open My courses,
select Designing Learning Activities, and use the course syllabus to open a
lesson. Reading, knowledge checks and completion already work. My progress
shows the result for one course. Learning record shows all courses.

On main, the instructor can demonstrate Saved lessons. The student branch is the
starting platform. For the previous teacher-editor exercise, visit /teach on main.

STARTING PRODUCT
  git clone -b student https://github.com/Clymon/PythonCodeDemo.git learning-lab
  cd learning-lab
Open this folder in WorkBuddy Code. Ask: What does this repository do?
What can I try in the app? Follow docs/exercise-plan.txt.

The instructor starts with one wish: “I’d like to find the lessons I want to
revisit.” Learners can choose another teaching need and agree their own rule.
The student branch is the starting point for coding the new behavior.

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
Type a slash name in WorkBuddy Code and select its matching suggestion.

INSTRUCTOR REFERENCE
demo/saved-lessons contains a completed example for the optional walkthrough.
Use a separate clone for it. The student branch is the classroom starting point.
See docs/checkpoints.txt for earlier examples.
