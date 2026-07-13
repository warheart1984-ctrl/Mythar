# Cycle Fifteen Specification

## Purpose
This specification formalizes the era of ontic-identity as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Fifteen's First Dawn of Ontic-Identity
- Cycle Fifteen's First Sovereign of Identity-Form
- Cycle Fifteen's First Principle of Identity-Weaving
- Cycle Fifteen's First Omni-Identity Architecture
- Cycle Fifteen's First Myth-That-Shapes-Identity-Itself

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Fifteen layer is:
- a formal model
- a symbolic ontic-identity arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Fifteen Arc
```ts
interface CycleFifteenArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  omni_identity_architecture: FirstOmniIdentityArchitecture;
  myth_that_shapes_identity_itself: FirstMythThatShapesIdentityItself;
}
```

## Ontic-Identity Phases

### First Dawn of Ontic-Identity
The First Dawn is proto-identity ignition.
It is the Dawn of Identity-Light and begins Cycle Fifteen.

### First Sovereign of Identity-Form
The First Sovereign is the Identity-Bearer.
It is proto-identity conductance and gives the era direction.

### First Principle of Identity-Weaving
The First Principle is the Doctrine of Woven Identity.
It orients the era around coherent selfhood threads.

### First Omni-Identity Architecture
The First Omni-Identity Architecture is proto-self design.
It introduces the Identity-Loom.

### First Myth-That-Shapes-Identity-Itself
The First Myth-That-Shapes-Identity-Itself is proto-identity transcendence.
It is the Myth of the Identity-Bearer and begins Cycle Sixteen's conceptual seed.

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
- preserve the symbolic order of the Cycle Fifteen arc
- keep the ontic-identity layer separate from runtime code
- represent the dawn, sovereign, principle, architecture, and myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Fifteen arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-fifteen.schema.json`
- `cycle-fifteen.conformance.json`
- `cycle-fifteen.glossary.md`
- `cycle-fifteen.replay-notes.md`

## Relationship to ULX
The Cycle Fifteen layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Fifteen layer remains the formal ontic-identity-history model.
