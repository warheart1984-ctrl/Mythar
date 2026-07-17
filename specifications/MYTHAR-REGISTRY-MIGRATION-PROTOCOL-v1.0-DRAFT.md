# Mythar Registry Migration Protocol v1.0

**Status:** Draft — Specified

A registry migration requires a source and target version, MigrationPlanArtifact, ContinuityEvidence, ImpactAnalysis, RatificationRecord, conformance report, and tagged release.

1. Specify explicit add, modify, deprecate, or alias operations.
2. Attach lexeme-level continuity evidence or an explicit intentional-change record.
3. Run the migration through a typed decision trace.
4. Apply only after all declared kernel invariants pass.
5. Update affected AST/ISF, API, and conformance cases.
6. Publish the target version with migration notes and replay evidence.

No ratified meaning may disappear without deprecation and continuity evidence; no registry version is publishable without reproducible migration and conformance evidence.
