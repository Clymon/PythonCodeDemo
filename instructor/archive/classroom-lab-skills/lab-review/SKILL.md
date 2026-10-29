---
name: lab-review
description: Compare a completed change against the learner-confirmed specification, collect relevant evidence and support a human acceptance decision.
---

Use this to review a task result or decide what verification is still needed.

1. Read the confirmed spec, decisions, selected task and Git diff. Make a short
   mapping from each acceptance example to evidence that could prove it.
2. Run relevant checks and inspect their assertions: what behavior would make
   them fail? Operate the browser, or ask for a specific human observation when
   tools cannot do it. Check a normal case and a boundary; check refresh/restart
   if saved state is part of the requirement.
3. Separate test output, observed browser behavior and inference. Report failures,
   regressions, untested paths and consequential design mismatches. If using
   backend coverage, explain its scope and one useful gap; avoid a target percent.
4. Update workshop/evidence.txt. Recommend accept/revise/continue with a reason,
   then leave the acceptance decision to the learner. A proposed fix is a new
   selected task unless already within the authorized implementation scope.

Complete when every task criterion is supported, contradicted or explicitly
unverified, and the learner can make an informed acceptance decision.
