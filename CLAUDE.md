# CLAUDE.md

@AGENTS.md

When you change a template file, render a variant and read the *output*, not just the source:

```sh
uvx copier copy --trust --defaults -r HEAD -d project_name=demo -d description=demo . /tmp/demo
```

Keep `-r HEAD`: without it Copier renders the latest release tag, not your working tree.
