# G2 Baseline Rules

## NaivePersistentState

This deliberately simple baseline keeps the latest matching symbolic record from
the incoming record stream as active belief, regardless of whether that record
came from current observation, reconstructed memory, or a future hypothesis. It
is included to stress stale state and source-confusion failures. It is not a
state-of-the-art baseline.

## ChronologicalRecordReasoner

This stronger symbolic control receives chronological records with explicit
source labels. For NOW queries it uses only current observed/inferred records and
detects multiple current containment targets as contradiction. For PAST queries
it uses reconstructed-memory records. For POSSIBLE_FUTURE queries it uses future
hypothesis records and preserves multiple possibilities.

If this control matches or beats NowMind, the result should be reported as such.
