# Cursor session greeting (multi-host)

Use this as a quick first message at the top of a fresh Cursor session:

```
You are working in ai-stack.
First: print hostname, current git branch, and git status short.
Second: tell me which host role this is (faithh/gen8/other) based on known topology.
Third: do not make commits unless I explicitly ask.
Fourth: keep runtime artifacts and secrets out of git.
```

Optional stricter variant:

```
Before any edits, run:
hostname && git branch --show-current && git status --short
If branch is main, create a feature branch before code changes.
```
