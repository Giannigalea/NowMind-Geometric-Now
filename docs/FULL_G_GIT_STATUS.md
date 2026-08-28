# Full-G Git Status

Date: 2026-08-28

Git was initialized in the repository root for the Full-G freeze package, but
an active `.git/` directory triggered a Codex desktop setup-refresh failure on
this machine. To keep the working session usable and avoid losing project
state, the initialized Git metadata was moved aside instead of deleted:

```text
tmp/git_disabled_due_codex_refresh_20260828_full_g/
```

The Git directory remains inspectable with an explicit work-tree command:

```powershell
git --git-dir=tmp\git_disabled_due_codex_refresh_20260828_full_g --work-tree=. status --short
```

Current state:

- Branch renamed from the default `master` to `main`.
- Baseline commit created after local Git identity was configured. Inspect the
  current `HEAD` of the preserved Git directory for the exact commit hash.
- Commit author identity:
  `Giannigalea <205990347+Giannigalea@users.noreply.github.com>`.
- The repository root intentionally does not contain an active `.git/`
  directory during this Codex desktop session.

To inspect the baseline commit:

```powershell
git --git-dir=tmp\git_disabled_due_codex_refresh_20260828_full_g --work-tree=. rev-parse HEAD
git --git-dir=tmp\git_disabled_due_codex_refresh_20260828_full_g --work-tree=. show --stat --oneline HEAD
```

If Codex desktop no longer fails on active Git metadata, the preserved Git
directory may be restored from `tmp/git_disabled_due_codex_refresh_20260828_full_g/`
to `.git/` outside this active session.
