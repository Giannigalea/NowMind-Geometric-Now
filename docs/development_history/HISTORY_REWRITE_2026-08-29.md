# History Rewrite: PCT Book Removal

Date: 2026-08-29

## Purpose

Git history was rewritten solely to remove the commercially published PCT book
PDF from the public repository's reachable history.

The removed file path was:

```text
reference/PCT_Book_Latest.pdf
```

No unrelated reference material, scientific code, benchmark prompts, scoring,
validators, result artifacts, or research conclusions were intentionally changed
by the history rewrite.

## Copyright Context

Present Consciousness Theory (PCT) is a separately published work by Jonathan
Galea. The full commercially published book is not distributed as part of this
public repository. This repository contains only material intentionally provided
as part of the NowMind Geometric Now research package.

## Backup

A local safety bundle was created outside the active repository before the
history rewrite. The backup is not part of the public repository.

## Path Discovery

Before rewriting history, the tracked current tree and reachable commit history
were searched for PDF/book paths. The only reachable book PDF path discovered was:

```text
reference/PCT_Book_Latest.pdf
```

No duplicate historical book filename/path was discovered.

## Commit Mapping

The following old commits were rewritten because they were downstream of the
removed book object:

| Meaning | Old commit | New commit |
|---|---|---|
| Full-G baseline | `8f4ef9742a90fbb11301d1f66b4d65e5a4efb78e` | `8a4c7a4315daf2f002de36e180922c72b479f9e5` |
| Public documentation cleanup | `485e5c876c1b67515c6d93a1c800a64c4d96ccc9` | `ba3698a01dcd96d4c7c848418a59bf805185e7f9` |
| PCT book/public package cleanup | `7400a8e4cfdd3c76a9de956b939c60be00289c72` | `c5dd357d8ef6f2ad4df719b36e605696ea8cc5eb` |

## Verification Intent

After the rewrite, reachable history should not contain
`reference/PCT_Book_Latest.pdf`, and the public repository should retain the
same scientific evidence package without redistributing the full PCT book.
