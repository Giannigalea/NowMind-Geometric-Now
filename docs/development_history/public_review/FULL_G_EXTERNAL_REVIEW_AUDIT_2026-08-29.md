# Full-G External Review Audit

Date: 2026-08-29

Audited cleanup commit: `485e5c876c1b67515c6d93a1c800a64c4d96ccc9`

Scope: public/external-review quality audit after the approved documentation cleanup. This audit does not change NowMind architecture, benchmarks, prompts, scoring, validators, scientific artifacts, or Git history.

## Executive Verdict

Overall readiness grade: **C**

The scientific package is preserved, unusually transparent, and test-backed, but the public-facing repository still reads partly like a development workspace rather than a polished external review package. The main blockers are missing license/attribution clarity and visible internal operating notes in root/reference/status material. The evidence base is strong enough to review technically, but not yet clean enough for a confident public release tag.

Recommendation: do not tag `full-g-v1.0` yet. Fix the blockers and high-priority public-documentation issues first.

## Cleanup Verification

- Approved README Development History cleanup completed: yes. The main `README.md` no longer contains a `Development History` section.
- Approved person-neutral cleanup completed: yes for reviewer-facing documentation. `docs/JULIAN_TECHNICAL_BRIEF_DRAFT.md` was renamed to `docs/EXTERNAL_TECHNICAL_BRIEF.md` and rewritten as a generic external technical brief.
- Cleanup commit hash: `485e5c876c1b67515c6d93a1c800a64c4d96ccc9`.
- Push to `origin/main` verified: yes. `origin/main` resolves to `485e5c876c1b67515c6d93a1c800a64c4d96ccc9`.
- Git history preserved: yes. Baseline commit `8f4ef9742a90fbb11301d1f66b4d65e5a4efb78e` remains reachable; no rewrite, squash, rebase, or force-push was performed.
- Current reviewer-facing tree contains named Julian/Michels references: no, excluding archived development-history task specifications.
- Current full HEAD contains those names anywhere: yes, only inside `docs/development_history/codex_tasks/` historical task files and in Git history. This was intentionally not rewritten.

## Verification Evidence

- Full pytest result before cleanup commit: `138 passed in 58.20s`.
- Secret scan result before cleanup commit: no live API key, GitHub token, `.env`, key file, or OpenRouter key literal was found in the tracked working tree outside ignored `tmp/` and caches.
- Git status after cleanup push: `main...origin/main` clean at `485e5c8`.
- Remote branch verification: `485e5c876c1b67515c6d93a1c800a64c4d96ccc9 refs/heads/main`.

## Audit Findings

### F-001 - BLOCKER - License and Attribution

- Category: License/attribution.
- Location: repository root, no `LICENSE`, `COPYING`, `NOTICE`, `CITATION`, or `AUTHORS` file present; `reference/PCT_Book_Latest.pdf`; `reference/missing_originals/ADD_LEGACY_NOWMIND_CODE_HERE.txt:2`.
- Issue: the repository does not state public reuse rights for code, docs, benchmark artifacts, or included source/reference material.
- Why a reviewer cares: a public technical reviewer cannot know what they are allowed to quote, reuse, fork, or redistribute. Included PDF/reference material raises additional attribution and rights questions.
- Recommended correction: add a clear license for original code/docs, a citation file, and a notice explaining which reference materials are included for review only, who owns them, and whether they may be redistributed.

### F-002 - BLOCKER - Internal Starter Pack in Root

- Category: First 60 seconds / development-method leakage / root cleanliness.
- Location: `00_READ_ME_FIRST.md:1-51`.
- Issue: the first root-level entry point still says the project is a starter context "with Codex" and includes implementation-agent authority rules.
- Why a reviewer cares: the public first impression is that this is an internal AI-build workspace, not a polished scientific package.
- Recommended correction: move this file to `docs/development_history/` or rewrite it as a neutral `ARCHITECTURE_START_HERE.md` focused on theory, evidence, and reviewer navigation.

### F-003 - SHOULD FIX - README Title and Stale G2.3 Framing

- Category: README / first 60 seconds / naming consistency.
- Location: `README.md:1-34`.
- Issue: the README title still says `G2.3`, and the G2.3 section says no Ollama runtime was installed in the environment.
- Why a reviewer cares: the repository has since been packaged as Full-G and includes later local-model evidence through G2.3.4. The stale framing makes the newest result unclear.
- Recommended correction: retitle the README as a Full-G package, keep the staged history, and replace the stale Ollama note with a concise pointer to G2.3.1-G2.3.4 outcomes.

### F-004 - SHOULD FIX - README Review Navigation Stops Before Full-G

- Category: Reviewer navigation.
- Location: `README.md:488` and following review-document list.
- Issue: the review documents list reaches the G2.3 docs but does not surface the Full-G reviewer entry points.
- Why a reviewer cares: the strongest public materials are `REPRODUCE_FULL_G.md`, `docs/FULL_G_RESULTS_SUMMARY.md`, `docs/FULL_G_CLAIMS_AND_NONCLAIMS.md`, `docs/FULL_G_NEGATIVE_RESULTS.md`, and `docs/EXTERNAL_TECHNICAL_BRIEF.md`, but they are not promoted in the main review path.
- Recommended correction: add a short "External Review Entry Points" block near the top and include the Full-G files before the detailed stage archive.

### F-005 - SHOULD FIX - Root STATUS File Is Too Operational

- Category: Development clutter / public presentation.
- Location: `STATUS.md:46-48`, `STATUS.md:200-206`.
- Issue: `STATUS.md` contains Codex desktop setup details, moved Git metadata paths, OpenRouter migration operational notes, and historical setup narrative.
- Why a reviewer cares: this obscures the scientific status and exposes unnecessary machine/workflow detail.
- Recommended correction: preserve the current file in development history and replace root `STATUS.md` with a concise public status page summarizing stages, artifacts, test status, and known limitations.

### F-006 - SHOULD FIX - Git Operational Note Is Public-Facing

- Category: Git tracking / development-method leakage / security/privacy.
- Location: `docs/FULL_G_GIT_STATUS.md:5-40`.
- Issue: this file documents Codex desktop setup failures, the disabled Git metadata directory, and the configured author identity.
- Why a reviewer cares: it is useful operational history, but not useful first-line public evidence and it exposes local workflow details.
- Recommended correction: move it under development history or rewrite it as a short public Git provenance note that only states commit lineage, remote status, and no history rewrite.

### F-007 - SHOULD FIX - Machine-Specific Paths Remain in Reviewer-Facing Files

- Category: Security/privacy / reproducibility.
- Location: `docs/G1_REPRODUCIBILITY.md:17`, `artifacts/g1/g1_test_results.txt:1`, plus Ollama provenance paths under `artifacts/g2_3_1/` and frozen G2.3.2 snapshots.
- Issue: some docs and artifacts include local absolute Windows paths such as `D:\Documents\...`, `C:\Users\jonat\...`, and `D:\OllamaModels`.
- Why a reviewer cares: paths can leak local usernames and machine layout, and they make reproduction instructions look machine-specific.
- Recommended correction: replace docs with repo-relative examples and keep machine-specific artifact provenance only where scientifically necessary, ideally behind an artifact manifest note.

### F-008 - SHOULD FIX - Development Language Outside Archive

- Category: Development-method leakage / person-neutrality.
- Location: `docs/OPEN_QUESTIONS.md:3`, `docs/GEOMETRIC_NOW_G1_SPEC.md:95`, `docs/G1_ACCEPTANCE_TESTS.md:3`, `reference/README_REFERENCE.md:3-38`, `reference/SOURCE_INDEX.md:12-43`, `reference/legacy_docs/RESEARCH_HANDOFF_NOTES.md:1-5`.
- Issue: several non-archived files still mention Codex, ChatGPT file-library reconstruction, or implementation-agent instructions.
- Why a reviewer cares: this distracts from the architecture and raises avoidable questions about whether the repo is a final research artifact or a prompt transcript.
- Recommended correction: preserve original history under `docs/development_history/` and rewrite public-facing reference notes as neutral provenance records.

### F-009 - SHOULD FIX - Placeholder and Template Text Still Visible

- Category: Placeholders / embarrassment check.
- Location: `docs/DECISIONS_LOG.md:55`, `reference/missing_originals/ADD_LEGACY_NOWMIND_CODE_HERE.txt:2`, `docs/DECISIONS_LOG.md:181`.
- Issue: placeholder/template entries are still visible in the public tree.
- Why a reviewer cares: placeholders make the repo look unfinished even when the scientific artifacts are complete.
- Recommended correction: move placeholders to development history, or label them explicitly as archived provenance rather than active reviewer material.

### F-010 - SHOULD FIX - Artifact Volume Needs a Public Index

- Category: Artifact quality / reproducibility / root cleanliness.
- Location: `artifacts/`, especially large tracked JSONL files such as `artifacts/g2_2/g2_2_trial_results.jsonl`.
- Issue: the repo tracks hundreds of artifact files, including multiple large raw benchmark outputs and frozen snapshots.
- Why a reviewer cares: preserving raw data is good, but without an index/checksum map it is hard to tell which artifacts are canonical and which are historical backups.
- Recommended correction: add an artifact manifest with canonical files, duplicate/frozen copies, byte sizes, checksums, and recommended reviewer order. Consider releases or Git LFS after the public baseline is tagged.

### F-011 - SHOULD FIX - Claims Are Strong but Not Front-Loaded

- Category: Claims-vs-evidence / negative results visibility.
- Location: `README.md:208-216`, `docs/FULL_G_CLAIMS_AND_NONCLAIMS.md`, `docs/FULL_G_NEGATIVE_RESULTS.md`.
- Issue: the claim boundaries are excellent in the dedicated docs, but the README does not lead with the Full-G claims/nonclaims and negative result summary.
- Why a reviewer cares: reviewers should understand immediately that this is a mechanistic architecture/reproducibility package, not a consciousness claim or a model-performance claim.
- Recommended correction: add a short top-level "What this does and does not claim" section with direct links to the claims and negative-results docs.

### F-012 - SHOULD FIX - OpenRouter Migration Doc Reads Like Sensitive Operational History

- Category: Security/privacy / development clutter.
- Location: `docs/G2_3_3_API_KEY_MIGRATION.md:9-14`, `docs/G2_3_3_BATCHING.md:15`.
- Issue: these files expose exact environment-variable workflow and failed Git/Codex operational history. No key is present, but the files remain operationally noisy for public review.
- Why a reviewer cares: even without secrets, API-key migration notes are not part of the scientific result and may make readers wonder if secret hygiene is complete.
- Recommended correction: move these notes to development history and keep only a public statement that paid APIs are frozen and no key material is tracked.

### F-013 - NICE TO HAVE - Full-G Demo Could Be More Self-Describing Without JavaScript

- Category: Full-G reviewer demo.
- Location: `http://127.0.0.1:8766/?demo=full_g_reviewer`; API `/api/demo` returns six expected Full-G sections.
- Issue: the runtime API returns the correct Full-G sections, but the static HTML does not expose those section titles before JavaScript state loads.
- Why a reviewer cares: reviewers using page search, static snapshots, or restricted browsers may miss the structure.
- Recommended correction: add a small static fallback heading/list for the Full-G reviewer demo while preserving the dynamic UI.

### F-014 - NICE TO HAVE - Add Citation Metadata

- Category: License/attribution / release readiness.
- Location: repository root.
- Issue: there is no `CITATION.cff` or recommended citation text.
- Why a reviewer cares: if the work is shared with researchers, they need a stable citation path.
- Recommended correction: add `CITATION.cff` once author, title, version, and license are finalized.

### F-015 - NICE TO HAVE - Add Reviewer Screenshots

- Category: First 60 seconds / Full-G reviewer demo.
- Location: root or `docs/`.
- Issue: the browser demo is available locally, but there is no screenshot/GIF preview in the README.
- Why a reviewer cares: a quick visual preview helps reviewers decide where to click first.
- Recommended correction: add one small screenshot of the Full-G reviewer dashboard and link it from the README.

### F-016 - NICE TO HAVE - Add Checksums for Key Artifacts

- Category: Reproducibility / scientific artifact quality.
- Location: `artifacts/full_g/`, `artifacts/g2_3_2/`, `artifacts/g2_3_4/`.
- Issue: benchmark artifacts are preserved, but there is no top-level checksum list for the canonical result files.
- Why a reviewer cares: checksums make the frozen status easier to verify independently.
- Recommended correction: add `artifacts/full_g/MANIFEST.sha256` or a similar generated manifest.

### F-017 - NICE TO HAVE - Clarify Explicit vs Latent Geometry Earlier

- Category: Explicit-vs-latent geometry terminology.
- Location: `docs/EXTERNAL_TECHNICAL_BRIEF.md`, `README.md`.
- Issue: the distinction is present in the technical brief, but the README does not quickly explain that NowMind uses explicit present-state relational geometry, not learned latent embedding geometry.
- Why a reviewer cares: this is central to avoiding confusion with mainstream model-internal representation geometry.
- Recommended correction: add a two- or three-sentence terminology note near the top of the README.

## Category Verdicts

1. First 60 seconds: SHOULD FIX. The repo is impressive but still starts with G2.3/starter-pack framing rather than a Full-G reviewer path.
2. Root cleanliness: SHOULD FIX. Root tracked files are few, but `00_READ_ME_FIRST.md` and root `STATUS.md` feel internal.
3. Development-method leakage: BLOCKER. Several public files still expose Codex/ChatGPT construction context.
4. Person-specific/outreach cleanup: PASS for reviewer-facing files; historical archived task specs still preserve old references.
5. README: SHOULD FIX. Strong content, stale title and environment note.
6. Claims/evidence alignment: PASS. The results and nonclaims are cautious and well-separated.
7. Negative results: PASS. Negative model-replication results are explicit and preserved.
8. Explicit vs latent geometry: SHOULD FIX. Scientifically clear in the technical brief, not front-loaded enough in README.
9. Reproducibility: SHOULD FIX. Commands exist, but machine-specific paths and artifact complexity reduce confidence.
10. Full-G reviewer demo: PASS with NICE TO HAVE fallback improvements.
11. Links/paths: SHOULD FIX. Conventional Markdown links were not broken, but many file references are plain text and some paths are local absolute paths.
12. Placeholders/TODOs: SHOULD FIX. Some placeholder/template notes remain visible.
13. Naming consistency: SHOULD FIX. Full-G packaging and README G2.3 title conflict.
14. Spelling/grammar: PASS with minor polish. No major credibility-damaging grammar issues found.
15. Security/privacy: SHOULD FIX. No live secret found, but local usernames/paths and API-key workflow notes remain.
16. Git tracking: PASS. Branch is pushed and clean at the cleanup commit; audit report is intentionally a new local file.
17. Git history/release: PASS for preserved history; SHOULD FIX before tagging because release metadata/license are incomplete.
18. License/attribution: BLOCKER.
19. Scientific artifact quality: PASS with SHOULD FIX artifact-index improvement.
20. Embarrassment check: SHOULD FIX. The project is scientifically strong, but a public reviewer will still see internal-build residue.

## Required 34-Item Summary

1. Approved README Development History cleanup completed? Yes.
2. Person-neutral cleanup completed? Yes for reviewer-facing documentation.
3. Current HEAD contains Julian/Michels refs? Yes only in archived development-history task specs; no in reviewer-facing paths outside `docs/development_history/`.
4. Person-specific outreach files remaining? No reviewer-facing outreach files remain.
5. Cleanup commit hash: `485e5c876c1b67515c6d93a1c800a64c4d96ccc9`.
6. Push to `origin/main` verified? Yes.
7. Full pytest result: `138 passed in 58.20s`.
8. Root verdict: SHOULD FIX.
9. README verdict: SHOULD FIX.
10. First-60-sec verdict: SHOULD FIX.
11. Reviewer navigation verdict: SHOULD FIX.
12. Claims-vs-evidence verdict: PASS.
13. Negative-results visibility verdict: PASS.
14. Explicit-vs-latent terminology verdict: SHOULD FIX.
15. Reproducibility verdict: SHOULD FIX.
16. Full-G reviewer-demo verdict: PASS with NICE TO HAVE static fallback.
17. Links/path verdict: SHOULD FIX.
18. Naming consistency verdict: SHOULD FIX.
19. Spelling/grammar verdict: PASS.
20. Security/privacy verdict: SHOULD FIX; no live secret found.
21. Git tracking verdict: PASS for pushed cleanup commit; this audit report is the only new local file.
22. Git history/release verdict: PASS for preserved history, SHOULD FIX before release tag.
23. License/attribution verdict: BLOCKER.
24. Scientific artifact verdict: PASS with artifact-manifest improvement recommended.
25. Development-clutter verdict: SHOULD FIX.
26. Person-neutrality verdict: PASS outside archived history.
27. BLOCKERS count: 2.
28. SHOULD FIX count: 10.
29. NICE TO HAVE count: 5.
30. Overall readiness grade A/B/C/D: C.
31. Five highest-priority remaining changes: add license/attribution notices; rewrite or archive `00_READ_ME_FIRST.md`; refresh README as Full-G reviewer entry point; move operational `STATUS.md`/Git/API-key notes into development history; add artifact manifest/checksums.
32. Recommend showing repo to external technical researcher RIGHT NOW? No for a polished public review. Yes only if framed as an early transparent work-in-progress.
33. Should `full-g-v1.0` be tagged after fixes? Yes, after the two blockers and high-priority SHOULD FIX presentation items are resolved.
34. Exact path to audit report: `D:\Documents\Codex Projects\NowMind-Geometric-Now\docs\FULL_G_EXTERNAL_REVIEW_AUDIT.md`.
