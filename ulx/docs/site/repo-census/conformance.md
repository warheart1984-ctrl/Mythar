# Repo Census and Batch Migration Conformance Mirror

This page mirrors the conformance expectations for the census and batch
migration surface.

## Conformance Expectations
- The manifest generator is deterministic.
- Pilot selection is repeatable for the same repository inventory.
- Collision detection blocks invalid batch compositions.
- Per-substrate reports and batch summaries are emitted for every run.

## Validation Surface
The runnable checks live in the ULX test suite, which exercises:
- census generation
- collision detection
- dry-run reporting
- pilot batch execution
