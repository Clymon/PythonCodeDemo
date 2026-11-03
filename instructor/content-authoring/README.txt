PREPARED CONTENT-MAINTENANCE REFERENCE — 3 November 2026

Source: main. This was implemented and checked by Codex, not executed through
WorkBuddy or claimed as a Matt Skill run. It illustrates one instructor choice;
participants choose their own scope and approach from the shared teaching goal.

Chosen slice: edit an existing lesson's title, objective and paragraphs; preview
without saving; save makes it visible immediately on the student page. Stable
course/chapter/lesson/question IDs and existing learning results remain unchanged.
Examples, resources and checks stay attached. No quiz editing, new-lesson creation,
import, draft/publish workflow or institutional account/ownership system is included.
Teaching demo is a local reference view, not an authenticated teacher role.

Operate: open /teach, select a course/lesson, change text, preview, verify the
student page is still unchanged, save, open the student page and reload. Invalid
or empty text must not replace the existing lesson. Saved changes survive a new
server instance using the same SQLite database. SQLite lesson_edits stores only
the selected text fields; the base catalog is preserved. Do not copy that storage
choice into a participant specification unless they deliberately choose it.

Evidence: 18 starting-product checks; 23 main-reference checks. Browser inspection
covers preview without saving, changed student view, refresh and responsive layouts.
The separate historical WorkBuddy trial also had 18 checks; that count belongs to
the old review feature and must not be conflated with the new LMS baseline count.

Possible next work is a human decision: richer content, creation, import or a
publishing workflow. Handoff should name the selected goal and evidence, not a
fictional fixed Ticket 02. Full completion is not required in the three-hour class.
