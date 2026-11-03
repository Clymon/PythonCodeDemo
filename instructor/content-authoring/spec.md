# Prepared example: edit existing lesson text

This is one instructor decision, not the class's prescribed specification.

## Problem
A teacher must ask a developer to update prepared lesson text. A small first result
lets the teacher update an existing lesson and students read the new material.

## Chosen behavior
Edit title, objective and ordinary paragraphs for an existing lesson. Preview
shows proposed text without storing it. Save validates and persists it, then the
student view reads the changed text. Saving is immediately visible in this example.
Stable content identity, resources, examples, question rules and learning records stay.

## Verification decisions
Use the HTTP interface for accepted/rejected saves, identity preservation and
restart persistence. Observe the actual browser for editing, preview and the
learner-visible result. These evidence scopes are distinct.

## Out of scope
New courses/chapters/lessons, imports, quiz editing, draft/publication transitions,
authenticated multi-teacher ownership and rich-text/media authoring.
