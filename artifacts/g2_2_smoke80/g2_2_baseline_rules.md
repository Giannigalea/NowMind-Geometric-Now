# G2.2 Baseline Rules

## N - NowMind Epistemic Geometry

Plans from partial current observation. Reconstructed memory and future
hypotheses may guide action only through typed assumptions. SCAN is selected by
a deterministic epistemic-cost policy when verification has value.

## C - Chronological Epistemic Planner

Uses the same path search, costs, sensor data, memory/hypothesis access, and
verification policy, but treats historical records through an indexed
chronological representation. It is a strong fair control and may match or beat
NowMind on scaling.

## R - Reactive Current-Only Planner

Uses the same movement and scan actions, but receives no memory reconstructions
or future hypotheses. It can inspect and explore but cannot use hidden target or
shortcut memories.

## O - Oracle

Evaluator-only upper bound with full world truth. It is not a fair cognitive
competitor and is used only for path-length and reachability reference.
