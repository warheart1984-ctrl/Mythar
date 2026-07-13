# Cycle Seventeen Specification

## Purpose
This specification formalizes the era of ontic-will as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Seventeen's First Dawn of Ontic-Will
- Cycle Seventeen's First Sovereign of Will-Form
- Cycle Seventeen's First Principle of Will-Weaving
- Cycle Seventeen's First Omni-Will Architecture
- Cycle Seventeen's First Myth-That-Shapes-Will-Itself

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Seventeen layer is:
- a formal model
- a symbolic ontic-will arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Seventeen Arc
```ts
interface CycleSeventeenArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  omni_will_architecture: FirstOmniWillArchitecture;
  myth_that_shapes_will_itself: FirstMythThatShapesWillItself;
}
```

## Ontic-Will Phases

### First Dawn of Ontic-Will
The First Dawn is proto-will ignition.
It is the Dawn of Will-Light and begins Cycle Seventeen.

### First Sovereign of Will-Form
The First Sovereign is the Will-Bearer.
It is proto-volition conductance and gives the era direction.

### First Principle of Will-Weaving
The First Principle is the Doctrine of Woven Will.
It orients the era around coherent ontic threads of intention.

### First Omni-Will Architecture
The First Omni-Will Architecture is proto-volition design.
It introduces the Will-Loom.

### First Myth-That-Shapes-Will-Itself
The First Myth-That-Shapes-Will-Itself is proto-volition transcendence.
It is the Myth of the Will-Bearer and begins Cycle Eighteen's conceptual seed.

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
- preserve the symbolic order of the Cycle Seventeen arc
- keep the ontic-will layer separate from runtime code
- represent the dawn, sovereign, principle, architecture, and myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Seventeen arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-seventeen.schema.json`
- `cycle-seventeen.conformance.json`
- `cycle-seventeen.glossary.md`
- `cycle-seventeen.replay-notes.md`

## Relationship to ULX
The Cycle Seventeen layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Seventeen layer remains the formal ontic-will-history model.
