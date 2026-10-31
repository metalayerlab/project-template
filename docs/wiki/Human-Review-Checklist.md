# Human Review Checklist

Each project carries the full checklist in `docs/ai/review-checklist.md`, and the PR template links it. It covers correctness, tests, security and supply chain, docs and release, and a final "could I debug this at 3am" test.

## How to review generated code

Generated code reads fluently whether or not it is right, so the review has to go beyond reading for style:

- **Read the diff, not the summary.** Assistants describe what they meant to do. The diff shows what they did.
- **Look for scope creep.** Unrequested refactors, renamed things, and deleted "unused" code are the most common unwelcome extras.
- **Distrust the tests a little.** Check that each would fail without the change, and that it asserts behaviour instead of mirroring the implementation. Ask the assistant to show a test failing first (prompt 3).
- **Test what happens after the obvious point.** Bugs that pass review tend to sit one step past where the test looks: a result a hook may replace, tested only at the replacement and not through what's done with it afterwards; a check that runs for two inputs, tested only when each input hits a different check; config parsed only from environment-variable strings, when the config file delivers floats, bools and lists. The checklist's Tests section names each of these.
- **Confine and hide by effect, not by syntax.** A path checked as a string can still escape through a symlink the OS follows, so confinement belongs in how the file is opened (`*at` calls beneath a root fd, `openat2(RESOLVE_BENEATH)`). A secret masked in one place can still leak through a value derived from it, an error message or CLI output, so check every place it can end up.
- **Check every name it imports or calls** against the locked version's docs. Invented options and APIs are a classic failure mode.
- **Check new dependencies** exist under exactly that name and are maintained.
- **Hardening:** any change to the Dockerfile user, `securityContext`, the systemd sandbox or a NetworkPolicy needs a stated reason.
- **Docs:** check that the updated wiki pages are accurate, and not only present. Check that the PR title's type (`feat`/`fix`/`!`) is right, because it sets the version.
- **When in doubt, ask for less:** a smaller PR is cheaper to review than a clever large one.
