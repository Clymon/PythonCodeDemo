---
name: lab-plan
description: Turn confirmed design decisions into a concise specification and small, independently verifiable development tasks.
---

Use this after a discussion has produced confirmed decisions.

1. Read workshop/decisions.txt and inspect current project facts as needed.
   Synthesize what is already agreed. If a missing decision blocks a task, ask
   that focused question rather than restarting the full interview.
2. Draft workshop/spec.txt using templates/spec.txt. Describe the user problem,
   behavior, examples, preserved rules and scope. Explain consequential technical
   choices in terms the learner can judge. Agree where and how results are checked.
3. Propose narrow, complete tasks. Each task must produce behavior someone can
   demonstrate independently and fit in a fresh session with its saved artifacts.
   Prefer one or two core tasks for this classroom exercise. Include verification
   in each task; front-end, API and database layers are implementation details,
   not separate delivery phases.
4. Present delivery, acceptance and real blockers for each task. Let the learner
   adjust granularity and dependencies. Save approved tasks as separate files in
   workshop/tasks/ using templates/task.txt; mark approval/status accurately.

Complete when the spec is confirmed and at least one task is ready to implement.
An open design question is a decision task, not permission to guess its answer.
