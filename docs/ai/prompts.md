# Prompts for working on the template

Copy-paste prompts for changing **this template** with an AI assistant that can read the repository. The
prompts that generated projects get are in [`template/docs/ai/prompts.md.jinja`](../../template/docs/ai/prompts.md.jinja).

They come from how recent changes were made: a generated project hits a wall in a template-owned file
(#52, #53, #56, #63), the fix gives every project a hook or a correct default, and the PR says exactly what
projects receive on `copier update` (#57, #58, #59, #61, #64).

Replace `<...>`. Each prompt ends where a human looks before work continues: keep that stop. Start each task
in a new session, and point to issues, files or failing checks by name rather than pasting them.

## 1. Triage a report from a generated project

Most work starts as an issue from a project that had to edit a template-owned file, or that broke on a fresh
render.

```text
Read AGENTS.md, docs/design/README.md and TODO.md (including "Decided
against"). Issue #<n>: <one line, or "read it with gh issue view">.

Don't change anything yet. Tell me:
1. Reproduce it: render the variant it names (-r HEAD) and show the failure,
   or explain why it doesn't reproduce.
2. Is it a bug (a fix:) or a missing hook (a feat:)?
3. Where the fix belongs: core (template/ or copier.yml), a layer value or
   fragment (layers/<lang>/), or both layers.
4. The mechanism, if it's a hook. For each, say why or why not:
   - a Copier answer (a build fact, like extra_ports or image_extras),
   - a project-owned file (project data the template never touches again,
     like contrib/system-packages.txt),
   - a fix to the template-owned file that removes the need for either.
5. Whether it needs a design record (a new question, a new project-owned
   file, or a choice with real alternatives does).
6. What every existing project sees on its next copier update.
Give your recommendation and why.
```

## 2. Design record

```text
Read AGENTS.md and docs/design/README.md, then the records it points to that
touch <area>. Write docs/design/<NNNN>-<short-title>.md from
template/docs/design/0000-template.md, Status: Proposed, for issue #<n>, and
add its row to docs/design/README.md.

Context: the project case from the issue, and the constraints that hold for
every change: a project that doesn't use the feature sees no diff on update;
the answers file and project-owned files are public interfaces.
Decision: exact names, types, defaults, validation, where each piece renders
(core or layer), what CI does, and the tests.
Alternatives considered: each with the concrete reason it lost.
Consequences: what projects get, what becomes permanent, and the wiki pages
that change.
Open questions: each with your recommendation.

Stop after the record. Don't write code.
```

## 3. Add a Copier question

The pattern of `extra_ports` (design [0005](../design/0005-extra-ports.md)) and `image_extras`
([0012](../design/0012-image-extras.md)).

```text
Read AGENTS.md. The design in docs/design/<NNNN>-<title>.md is approved
(with these changes: <...>). Implement it:

1. copier.yml: the question with type, default, help (what it is, an example,
   any caveat), a `when` that asks it only where it applies, and a validator
   that rejects anything that could reach a shell line or file as syntax.
2. Render it where the design says. With the default, the rendered project
   must be byte-for-byte what the last release renders. Prove it: render
   -r <last tag> and -r HEAD with the same answers, diff them, and show me
   that only .copier-answers.yml differs.
3. tests/test_render.py: accepted values (default, several, any special
   form), rejected values (wrong type, empty, injection, repeats), and a
   -m docker test if it changes the image.
4. Wiki: docs/wiki/Answering-the-Questions.md, the page for the area it
   changes, and the copier update -d command in
   Updating-from-the-Template.md.
5. Status: Implemented in the record and docs/design/README.md. Rejected
   alternatives go in TODO.md "Decided against", one line each with a link.

Run the Definition of done. Then stop and draft the PR body with prompt 8.
```

## 4. Add a project-owned file or hook

The pattern of `contrib/system-packages.txt` (#59) and `.github/repository.toml` (#54).

```text
Read AGENTS.md and layers/README.md. Implement <file> as decided in
<design record or issue #n>.

- Add it to _skip_if_exists in copier.yml, and write down why it must be
  project-owned: projects must diverge from it, and the template never needs
  to change it after the first copy. Keep the logic that reads it
  template-owned, so that logic keeps receiving fixes.
- Seed it so an existing project behaves exactly as before (empty lists, the
  current values).
- Wire it into every layer, or into the core once if it's language-neutral.
  Guard on the layer value, never on the language. Render each layer before
  and after and diff, so a layer that doesn't use it doesn't change.
- If projects should know it exists, add the AGENTS.md row and give its
  character count and category.
- Test: every variant renders the seed, and a test proves the hook works
  (-m docker if it's the image).
- Wiki: the pages it affects, Project-Layout.md, and the layers/README.md
  contract if layers must provide something.

Run the Definition of done, then stop and draft the PR body with prompt 8.
```

## 5. Fix a bug a generated project hit

```text
Read AGENTS.md. Bug #<n>: <what the project saw>.

1. Make a test variant in tests/test_render.py exhibit it (for #58 that was
   a long description with quotes, a backslash and a hyphen), and show me the
   render or check failing before any fix.
2. Find every place the same value or pattern is rendered, in every layer,
   not only the one reported: list them with file:line.
3. Fix it with the smallest change in each place. Prefer the layer contract's
   approach (read it at run time, tojson, escape) to working around one
   formatter.
4. Remove any TODO.md line this fixes, add a Troubleshooting entry if a
   project could still hit it, and update the wiki page that describes the
   behaviour.
5. In the PR body: the root cause, and what let it ship (the missing test or
   check).
Run the Definition of done, then stop.
```

## 6. Change a workflow or guard rail

For `.github/workflows/`, `scripts/` and `.claude/settings.json` under `template/`.

```text
Read AGENTS.md and the design records for <area> (docs/design/README.md
lists them). Change: <what and why, issue #n>.

- Pin every action to a commit SHA with the version in a trailing comment.
- Least privilege: say which permissions each job gets, and use
  GITHUB_TOKEN only; no new secret unless the design says so.
- Idempotent: a step that creates something (labels, metadata) runs safely
  every time (--force, check-then-create).
- A first push to a new repository must still pass: no wiki yet, no labels,
  no release.
- For deny rules, list what they block and what still gets through, and
  name the real control (the main ruleset, the token's permissions).
- Add a test that fails if a workflow relies on something nothing creates
  (like test_labels_are_created).
Run actionlint and the Definition of done, then stop and draft the PR body
with prompt 8.
```

## 7. Change template/AGENTS.md.jinja

```text
Read AGENTS.md, docs/design/0006-context-budget-review.md and
docs/wiki/Contributing-to-the-Template.md "Changing AGENTS.md". I want
projects' AGENTS.md to <rule or change>.

Before editing, measure the rendered AGENTS.md for every variant. Then:
- Add the shortest wording a new contributor reads right the first time.
  Its reason goes in the project wiki, not in AGENTS.md.
- If it doesn't fit, propose cuts, each with its category (1-8 from the wiki)
  and what an assistant would do differently without it. Only categories
  1-3 without measuring.
- Report the characters added and freed per variant, and the headroom left
  against the 75% ceiling.
Stop before making any cut in categories 4-8.
```

## 8. Write the PR body

```text
Draft the PR for this branch against main. Title: a Conventional Commit
describing the effect on projects (feat:, fix:, ! if a project's CI fails
after the update). Body, in this order, omitting none:

Closes/Fixes #<n>. Design record link, if there is one.
The project case in one or two sentences: what it couldn't do, and why.
## What projects get: each change, where it renders, and the behaviour with
   the default (prove "no diff" if you claim it).
Then one line each, stated even when the answer is "none":
- files that become project-owned, and why;
- the AGENTS.md character delta and its category;
- new required wiki pages or headings in .standard.toml (and the skeleton
  page you added);
- the wiki pages changed.
## Tests: the new tests, and every Definition of done command with its
   result. Name any failure, show it, and say why it's unrelated; never
   call a check passed that you didn't run.

No AI credit lines. Show me the draft; don't push or open the PR.
```

## 9. Review a template PR

```text
Review this branch against main (or PR #<n>) as a second reviewer. Read
AGENTS.md first. Report only concrete problems, each with file:line and why
it matters, most severe first. Check in particular:

- Rendered output, not source: render the affected variants and read them.
  Whitespace from trim_blocks, a stray [[ in a .jinja file, a line over the
  formatter's limit.
- Projects that don't use the change see no diff on update.
- Language-specific content in a core file, or a guard on language rather
  than on a layer value.
- Validators: can any accepted answer reach a shell line, a flag or TOML
  as syntax?
- Tests that would fail without the change, for every layer it touches.
- Unpinned actions, broader permissions, new secrets.
- _skip_if_exists changes without a reason in the PR.
- The wiki, the design record status, docs/design/README.md and TODO.md
  agree with the code, and nothing in TODO.md is now stale.
- The PR body claims (no diff, +0 characters, tests passed) are true.
Don't fix anything.
```

## 10. Upstream a local edit from a project

For when a project has had to edit a template-owned file.

```text
Read AGENTS.md. Project <owner/repo> at template version <_commit from its
.copier-answers.yml> has local edits to template-owned files. Here is how to
see them: <path to a checkout>.

Render the template at that version with the project's answers, diff it
against the project's checkout, and keep only template-owned files (not in
_skip_if_exists). For each local edit:
- what it does, and whether other projects would need it too;
- whether it would conflict with a template change on the same lines;
- the best way to remove it: a fix, a Copier answer, a project-owned file,
  or "keep it, it's specific to that project".
Draft one issue per edit worth upstreaming, in the Template problem or
Feature request form (.github/ISSUE_TEMPLATE/). Stop: don't open them.
```

## 11. After a merge

```text
Read AGENTS.md. PR #<n> was merged. Check that the repository records what
it should:
- every design record's Status matches the code, and docs/design/README.md
  matches the records;
- every Approved record with work left has a TODO.md line or an issue;
- no TODO.md line is already done (search git log for it);
- the issues the PR closes are closed;
- the release PR, if any, describes the change correctly.
Then answer: what let the original problem happen, and should template/, a
check or AGENTS.md change? Give your recommendation, or say "none".
List the changes; make them only after I agree.
```
