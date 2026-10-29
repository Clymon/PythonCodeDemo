---
name: lab-implement
description: Implement one approved classroom task with a complete user-visible result, incremental behavior checks and a clear evidence report.
---

Use this for a selected task whose design decisions and acceptance are ready.

1. Read the selected task, workshop/spec.txt, workshop/decisions.txt and current
   Git state. Identify one observable behavior and its agreed verification boundary.
   Resolve a genuine policy conflict with the learner; investigate code facts yourself.
2. For that behavior, add one meaningful check and run it. Confirm failure concerns
   the missing behavior, not a setup problem. Implement the smallest complete path
   and rerun the check. Add the next behavior only after this one works.
3. Exercise the actual page and persistence when required. Run relevant checks
   during work and the full Python suite after the selected task is complete.
   If browser tools are unavailable, give exact human check steps and mark browser
   results unverified until someone observes them.
4. Inspect the diff for scope and preserved behavior. Record commands, results,
   observed behavior and gaps in workshop/evidence.txt using templates/evidence.txt.
   Report the task result for human acceptance; make a checkpoint when requested.

Complete when the approved task's criteria are verified or a specific remaining
criterion is reported incomplete. Keep work in the chosen exercise folder.
Publishing or pushing requires the learner's request. Test count and coverage
percentage do not replace evidence for the requested behavior.
