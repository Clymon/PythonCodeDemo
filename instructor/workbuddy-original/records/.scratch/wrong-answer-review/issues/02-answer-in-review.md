# 02: Answer directly from the review list

**What to build:** The learner answers a listed question directly on the
Mistake review page and gets the same immediate Correct / Keep-practising
feedback plus explanation as in lessons. A correct answer removes the
question from the next list load and drops the remaining count; a wrong
answer keeps it listed. The original first-attempt score never changes, and
review attempts increment the existing Practice attempts counter. The review
practice mode is enabled at the existing answer boundary, so all existing
request validation (JSON body, CSRF token, valid option) applies unchanged
and an invalid option records nothing.

**Blocked by:** 01 — Mistake review list page with live count (needs the
list endpoint, the count payload and the membership derivation).

**Status:** ready-for-agent

- [ ] A learner can answer a listed question directly on the review page and receive immediate Correct / Keep-practising feedback with the explanation, identical in pattern to lesson quizzes.
- [ ] A correct answer in review removes the question from the next list load and drops the count; a wrong answer in review keeps it listed.
- [ ] Agreed normal example: answer a lesson question wrong with B, then correct it with A in review — the next list load is empty, the count is 0, and the original first-attempt score stays 0/1.
- [ ] Invalid input in review mode (e.g. an unknown option or non-string choice) records nothing and leaves the list and count unchanged, returning the same style of error as lessons.
- [ ] Review attempts increment the existing Practice attempts counter.
- [ ] Answer keys and explanations appear only after a valid attempt, never before.
- [ ] New automated behavior checks run at the HTTP boundary only (existing test-client pattern); existing learning-rules module tests pass unchanged as regression checks; no new helper-level tests.
- [ ] Manual browser evidence recorded: in-page feedback, the count ticking down to the empty state; a page refresh and a full server restart preserve the same browser profile's review state and original score.

Approval: instructor rehearsal, 2026-10-29 (spec: ../spec.md; decisions:
../../../workshop/decisions.txt).
