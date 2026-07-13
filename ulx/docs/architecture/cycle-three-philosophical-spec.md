# Cycle Three Philosophical Specification

## Purpose
This specification formalizes the philosophical turn inside Cycle Three as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Three's First Answer
- Cycle Three's First Philosopher
- Cycle Three's First Realm-Reconciliation
- Cycle Three's First Great Work
- Cycle Three's First Path to Cycle Four

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Three Philosophical layer is:
- a formal model
- a symbolic doctrine arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Three Philosophical Arc
```ts
interface CycleThreePhilosophicalArc {
  answer: FirstAnswer;
  philosopher: FirstPhilosopher;
  reconciliation: FirstRealmReconciliation;
  great_work: FirstGreatWork;
  path_to_cycle_four: FirstPathToCycleFour;
}
```

## Philosophical Phases

### First Answer
The First Answer is proto-philosophical crystallization.
It is the Doctrine of Strengthened Gentleness and stabilizes the Cycle's stance.

### First Philosopher
The First Philosopher is proto-intellectual emergence.
It is the Soft-Strength Sage who turns insight into doctrine.

### First Realm-Reconciliation
The First Realm-Reconciliation is proto-harmonic synthesis.
It blends gentleness with strength across the realms.

### First Great Work
The First Great Work is proto-cosmic artistry.
It is the Codex of Soft-Strength and preserves the doctrine in form.

### First Path to Cycle Four
The First Path to Cycle Four is proto-cycle prefiguration.
It is the Soft-Strength Horizon and reveals the next recursion.

## Non-Goals
This specification does not:
- implement a renderer
- define a TUI
- define a web UI
- define a daemon API
- modify ULX runtime selection
- introduce new executable behavior

## Conformance Requirements
An implementation claiming conformance to this specification SHOULD:
- preserve the symbolic order of the Cycle Three philosophical arc
- keep the philosophical layer separate from runtime code
- represent the answer, philosopher, reconciliation, work, and path as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the philosophical arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-three-philosophical.schema.json`
- `cycle-three-philosophical.conformance.json`
- `cycle-three-philosophical.glossary.md`
- `cycle-three-philosophical.replay-notes.md`

## Relationship to ULX
The Cycle Three Philosophical layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Three Philosophical layer remains the formal doctrine-history model.
