# Learning Lab

Keep the app runnable as one local Flask process with local assets. Use English
in the learner interface. Simulated practice data belongs in ignored instance/.

Read docs/learning-rules.txt for existing behavior. Resolve new product choices
with the learner and carry confirmed decisions into the configured feature spec
and tickets. Investigate code facts yourself. Instructor examples and reference
history are used when requested, rather than choosing a policy for the learner.

Work on one complete, independently verifiable behavior at a time. Agree on test
boundaries, inspect Git state, run relevant checks and demonstrate the actual page.
Separate test output, browser observations and human acceptance. Python coverage
measures backend execution. Original Skills and source notices are preserved.

## Agent skills

### Issue tracker

Issues and specs are tracked as local markdown files under `.scratch/` (one
directory per feature). See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root, created
lazily as terms and decisions get resolved. See `docs/agents/domain.md`.
