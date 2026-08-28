# Source Materials to Add Before/While Using Codex

The starter pack gives Codex the computational rules, but source material should be added so it can understand the wider PCT/NowMind project.

## Highest priority

### 1. Latest PCT book
Add the **latest authoritative version only** if possible.

Recommended path/name:

```text
reference/PCT_Book_Latest.pdf
```

If several editions exist, do not dump them all into the root without explanation. Put older versions under:

```text
reference/archive/pct/
```

and add a note identifying the latest authoritative edition.

Why:
The book is the philosophical source of truth for PCT terminology, Waterfall perspective, identity, memory, dreams, and quantum discussion.

### 2. Existing NowMind source code
Provide the latest working NowMind repository or ZIP.

Recommended:

```text
reference/legacy_nowmind/
```

or, if it is a ZIP:

```text
reference/legacy_nowmind_latest.zip
```

Important:
Legacy code is reference material at first. Codex must not blindly port it into G1 because some old mechanisms may violate the stricter Present Geometry boundary.

### 3. Existing NowMind architecture/design documents
Add any:
- README;
- architecture notes;
- version notes;
- specifications;
- whitepapers;
- diagrams;
- benchmark reports;
- explanations of L1/L2/L3;
- AICU/Veto Gate notes;
- GLIM-N+ or other later experimental notes if you want them preserved.

Recommended:

```text
reference/legacy_docs/
```

## Valuable supporting material

### 4. PCT whitepaper / academic-form manuscript
If different from the book, add it.

### 5. PCT glossary or terminology notes
Especially useful if the book contains evolving terms.

### 6. Relevant prior research correspondence
Only if it contains technical explanations not already in the book.

Do not add private emails merely for volume.

### 7. Screenshots of old NowMind UI
Optional.

Useful for future interface continuity, but not needed for G1 core logic.

## What NOT to upload merely for context

Avoid giving Codex:
- your entire ChatGPT export;
- hundreds of unrelated conversations;
- every obsolete NowMind build without labels;
- duplicated PCT book editions with no authority order;
- unrelated personal files.

More context is not always better. Contradictory uncurated context causes drift.

## Create a source index

After adding the real files, edit or ask Codex to update:

```text
reference/SOURCE_INDEX.md
```

For each source record:

```text
Name:
Path:
Date/version:
Authoritative? yes/no
Purpose:
Relevant topics:
Known conflicts/superseded material:
```

## Recommended minimum before serious G2/G3 work

Before moving past G1, Codex should have:
- latest PCT book;
- latest NowMind code;
- latest NowMind architecture notes;
- any existing memory/identity/veto specifications;
- benchmark/result notes that you still consider valid.

## Critical rule

The book should provide philosophical context, but **`PCT_COMPUTATIONAL_RULES.md` governs software behavior** unless Jonathan explicitly changes it.

This prevents Codex from interpreting metaphorical prose as implementation requirements.
