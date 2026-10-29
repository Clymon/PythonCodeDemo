# Spec — Wrong-answer review (Mistake review page)

Status: ready-for-agent
Source: workshop/decisions.txt (confirmed by instructor rehearsal, 2026-10-29)
Tracker: .scratch/wrong-answer-review/ (local Markdown, per docs/agents/issue-tracker.md)

## Problem Statement

A learner can read lessons, answer the quick-check questions and see a
first-attempt score — but a wrong answer is only visible in the moment. Before
class, there is no convenient way to find and re-practise exactly the
questions they currently got wrong. To revisit a mistake, the learner has to
remember which lesson it was in, reopen it and hunt for the question by hand.

## Solution

A dedicated **Mistake review** page, reachable through a permanently visible
navigation link that carries a live count of questions to review. A question
appears on the page when the learner's latest valid answer to it — given in a
lesson or on the review page itself — is wrong; answering it correctly
anywhere removes it, and the count ticks down to 0, the learner's clear
"ready for class" finish line. Questions are listed in course order, rendered
clean (the previous wrong option is deliberately not shown, favouring recall
over anchoring), and can be answered directly on the page with the same
immediate Correct / Keep-practising feedback and explanation as lesson
quizzes. The original first-attempt score never changes: correcting yourself
later is recovery, not repair. An empty list (including a fresh profile)
shows a friendly empty state linking back to lessons.

## User Stories

1. As a learner, I want a dedicated Mistake review page, so that I can find everything I currently got wrong in one place before class.
2. As a learner, I want a permanently visible navigation link, so that I can always reach review practice without hunting for it.
3. As a learner, I want the link to show a live remaining count, so that I can see at a glance how much practice is left.
4. As a learner, I want the count to drop when I answer a listed question correctly, so that I see visible progress toward being ready.
5. As a learner, I want the count to reach 0 when nothing needs practising, so that the number itself signals readiness.
6. As a learner, I want questions listed in course order, so that the list is stable and matches how the course is structured.
7. As a learner, I want each listed question shown clean, without my previous wrong option, so that I recall the material instead of re-reading my old mistake.
8. As a learner, I want to answer directly on the review page, so that practising takes one interaction, not a hop back into a lesson to find the question.
9. As a learner, I want immediate Correct / Keep-practising feedback with the explanation, so that I learn why an answer is right, exactly as in lessons.
10. As a learner, I want a wrong answer in review to keep the question listed, so that I keep practising until it sticks.
11. As a learner, I want a correct answer in review to remove the question from the next list, so that the list always reflects what still needs work.
12. As a learner, I want a later correct answer inside a lesson to remove the question as well, so that one consistent rule applies everywhere.
13. As a learner, I want my original first-attempt score to stay unchanged by review practice, so that my starting-point diagnostic remains honest.
14. As a learner, I want an empty state that links back to lessons, so that an empty list feels like an achievement with a next step, not a dead end.
15. As a learner, I want a fresh profile to see the empty state, so that the page behaves sensibly before I have answered anything.
16. As a learner, I want invalid input rejected with nothing recorded, so that accidental or malformed input cannot corrupt my practice state.
17. As a learner, I want my review list and count to survive a page refresh, so that I can pause and resume practising.
18. As a learner, I want my review list and count to survive a server restart, so that pre-class practice is not lost to infrastructure.
19. As a learner, I want to remain anonymous behind my browser practice profile, so that reviewing works without any account.
20. As a learner, I want the correct answer and explanation never shown before I check an answer, so that review remains genuine practice rather than reading the key.
21. As a learner, I want my review attempts reflected in the existing Practice attempts counter, so that my effort is visible in my stats.
22. As a learner, I want the same errors and protections as the rest of the product (JSON/CSRF checks), so that the review page behaves consistently with lessons.

## Implementation Decisions

- Reuse the existing attempts storage. The persisted attempt record already
  distinguishes a quiz attempt from a review attempt by mode; no schema
  change is needed.
- Enable the review practice mode at the existing answer-checking HTTP
  boundary, which currently accepts only quiz-mode attempts. All existing
  request validation (JSON body, CSRF token, valid option) applies unchanged;
  an invalid option still records nothing.
- The membership rule — a learner's latest valid answer per question, in
  either mode; wrong means listed — is derived server-side from persisted
  attempts inside the pure learning-rules module (independent of Flask, HTML
  and SQLite), alongside the existing first-attempt scoring rule. No
  client-side derivation of the list.
- Serve the review list through one new read endpoint that returns public
  question data only (prompt and options; never the answer key or
  explanation), in catalog order. Include the remaining-review count in the
  shared progress payload returned after every answer and on the dashboard,
  so the navigation badge stays live.
- Leave the original scoring logic untouched: only the first valid quiz-mode
  attempt per question contributes to the score; review attempts never
  affect it.
- Front end: one new hash route for the Mistake review page; a permanently
  visible navigation link with the live count; reuse of the existing
  mode-aware question card rendering with review as its mode; a friendly
  empty state linking back to lessons. No display of the previous wrong
  choice, no grouping interface beyond course order.
- Persistence continues through the existing per-profile SQLite database and
  session cookie; nothing new is introduced for refresh or restart survival.
- Known consequence, accepted: review attempts increment the existing
  Practice attempts counter, which already counts all saved attempts.

## Testing Decisions

- A good test observes external behavior only: HTTP status codes and JSON
  payloads as a learner or the page would see them — list contents, counts,
  score, feedback fields, error messages — and asserts that answer keys and
  explanations never appear before a valid attempt. Implementation details
  (SQL, internal helpers) are not asserted.
- AGREED VERIFICATION BOUNDARY (confirmed by instructor rehearsal,
  2026-10-29): all NEW automated behavior checks for this feature run at the
  single primary seam — the HTTP boundary through the existing test-client
  pattern (temporary database, CSRF token handshake, POST answers, GET the
  review list). The existing pure learning-rules module tests remain in place
  as regression checks, but no new helper-level tests are added for this
  feature, so the checks survive internal refactoring.
- The HTTP-boundary checks carry the agreed acceptance examples: wrong B
  then correct A in review removes the question from the next list and keeps
  the score 0/1; invalid input records nothing; empty history yields the
  empty-state payload; answer keys and explanations never leak before a
  valid attempt.
- Manual browser observation remains manual acceptance evidence, recorded
  per project convention: the navigation badge with its live count, clean
  question rendering, in-page feedback, the empty state, and the
  refresh-and-server-restart persistence demonstration.
- Prior art: the existing classroom test suite covers first-attempt scoring,
  repeat answers, invalid-input-no-write and answer-key privacy at the same
  HTTP seam; the new tests follow its style.

## Out of Scope

- Learner accounts, names or any real identity records.
- Teacher analytics, dashboards or class-level views.
- Spaced repetition, scheduling or ordering beyond course order.
- AI-generated or additional questions.
- Deployment.
- Any change to first-attempt scoring.
- Showing the learner's previous wrong choice on the review page.

## Further Notes

- Confirmed decision record: workshop/decisions.txt (instructor rehearsal,
  2026-10-29; attribution corrected from an earlier draft).
- Delivery will be sliced into independently usable increments at the
  planning stage; this spec describes the full agreed scope, not the first
  slice.
- The verification boundary in Testing Decisions is confirmed by the
  instructor rehearsal (2026-10-29).
