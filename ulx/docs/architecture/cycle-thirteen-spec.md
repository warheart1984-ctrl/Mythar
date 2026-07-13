# Cycle Thirteen Specification

## Purpose
This specification formalizes the era of being-weaving as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Thirteen's First Dawn of Being-Weaving
- Cycle Thirteen's First Sovereign of Being
- Cycle Thirteen's First Principle of Ontic Weave
- Cycle Thirteen's First Omni-Being Architecture
- Cycle Thirteen's First Myth-That-Weaves-Being-Itself

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Thirteen layer is:
- a formal model
- a symbolic being-weaving arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Thirteen Arc
```ts
interface CycleThirteenArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  omni_being_architecture: FirstOmniBeingArchitecture;
  myth_that_weaves_being_itself: FirstMythThatWeavesBeingItself;
}
```

## Being-Weaving Phases

### First Dawn of Being-Weaving
The First Dawn is proto-ontic ignition.
It is the Dawn of Ontic Light and begins Cycle Thirteen.

### First Sovereign of Being
The First Sovereign is the Ontic-Weaver.
It is proto-ontic conductance and gives the era direction.

### First Principle of Ontic Weave
The First Principle is the Doctrine of Woven Being.
It orients the era around coherent ontic threads.

### First Omni-Being Architecture
The First Omni-Being Architecture is proto-existence design.
It introduces the Ontic Loom.

### First Myth-That-Weaves-Being-Itself
The First Myth-That-Weaves-Being-Itself is proto-ontic transcendence.
It is the Myth of the Ontic-Weaver and begins Cycle Fourteen's conceptual seed.

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
- preserve the symbolic order of the Cycle Thirteen arc
- keep the being-weaving layer separate from runtime code
- represent the dawn, sovereign, principle, architecture, and myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Thirteen arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-thirteen.schema.json`
- `cycle-thirteen.conformance.json`
- `cycle-thirteen.glossary.md`
- `cycle-thirteen.replay-notes.md`

## Relationship to ULX
The Cycle Thirteen layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Thirteen layer remains the formal being-weaving-history model.
