# 01: Mistake review list page with live count

**What to build:** A learner whose latest valid answer to a question is wrong
finds it on a new, dedicated Mistake review page — reachable through a
permanently visible navigation link carrying the live remaining count.
Questions appear in course order, rendered clean (prompt and options only —
no answer key, no previous wrong choice), and each listed question links back
to its existing lesson, so this first slice already lets a learner retry
through the ordinary quiz in the lesson. No inactive or disabled answer
buttons are exposed on the list. A fresh profile or a fully corrected list
shows the friendly empty state linking back to lessons. The remaining count
also appears in the shared progress payload, so the badge stays live.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A fresh profile sees the empty state on the review page, with count 0, and no error.
- [ ] After a wrong quiz answer, the review list shows that question with public fields only (identifier, prompt, options), in catalog order.
- [ ] Each listed question links back to its existing lesson; the list itself exposes no answer controls (no inactive buttons).
- [ ] The remaining count appears in the navigation link and in the shared progress payload, and stays live.
- [ ] A later correct quiz answer (re-answered inside the lesson) removes the question from the next list load, since the latest valid answer in either mode decides membership.
- [ ] Answer keys and explanations never appear in any list payload.
- [ ] The original first-attempt score is unchanged by anything in this slice.
- [ ] New automated behavior checks run at the HTTP boundary only (existing test-client pattern); existing learning-rules module tests pass unchanged as regression checks; no new helper-level tests.
- [ ] Manual browser evidence recorded: permanently visible navigation link with live count, clean question rendering, lesson links, empty state; a page refresh and a full server restart preserve the same browser profile's list and count.

Approval: instructor rehearsal, 2026-10-29 (spec: ../spec.md; decisions:
../../../workshop/decisions.txt).

## Comments

### Implementation record (agent, 2026-10-29)

Ticket 1 implemented on branch `rehearsal/matt-original` via the original
implement Skill (tdd loop at the agreed HTTP seam, then code-review).

**Test output** (`.venv/bin/python -m unittest tests.test_app -v`, 18 tests):
13 pre-existing tests pass unchanged (pure additions in a new
`ReviewListTests` class; no existing test edited); 5 new HTTP-boundary checks:
fresh profile empty payload and count 0 (also in dashboard payload), wrong
answers list questions with public fields only in catalog order with lesson
link, correct quiz re-answer removes the question and keeps first-attempt
score 0/1 with live count, invalid answer changes nothing on the list, and
raw review payload never contains answer keys or explanations.

**Browser observations** (playwright-cli against `python app.py --port 5051`):
fresh profile shows nav link "Mistake review 0" and the friendly empty state
linking back to lessons; a wrong lesson answer ticks the badge to 1 live
without reload; the review page renders prompt + options only — no answer
controls, no previous wrong choice — with "Lesson 01/02" links and "Retry in
lesson" buttons; two wrong answers (lessons 01, 02) list both questions in
course order with badge 2; a full page refresh and a full server restart both
preserve the same browser profile's list and count; correct re-answers inside
the lessons drop the badge 2 → 1 → 0 and the page returns to the empty state,
while My progress still shows the original first-attempt score 0/2.

**Human acceptance**: still open — instructor to check the boxes above after
reviewing the commit and the running page.

