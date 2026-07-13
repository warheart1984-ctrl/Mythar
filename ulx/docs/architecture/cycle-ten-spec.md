# Cycle Ten Specification

## Purpose
This specification formalizes the era of world-weaving as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Ten's First Dawn of World-Weaving
- Cycle Ten's First Sovereign of Worlds
- Cycle Ten's First Principle of Cosmogenic Craft
- Cycle Ten's First Poly-World Architecture
- Cycle Ten's First Myth-That-Shapes-Cosmos

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Ten layer is:
- a formal model
- a symbolic world-weaving arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Ten Arc
```ts
interface CycleTenArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  poly_world_architecture: FirstPolyWorldArchitecture;
  myth_that_shapes_cosmos: FirstMythThatShapesCosmos;
}
```

## World-Weaving Phases

### First Dawn of World-Weaving
The First Dawn is proto-cosmogenic ignition.
It is the Dawn of Interwoven Light and begins Cycle Ten.

### First Sovereign of Worlds
The First Sovereign is the Cosmos-Loom Keeper.
It is proto-cosmic weaving conductance and gives the era direction.

### First Principle of Cosmogenic Craft
The First Principle is the Doctrine of Interwoven Creation.
It orients the era around worlds that interconnect coherently.

### First Poly-World Architecture
The First Poly-World Architecture is proto-cosmic structure.
It introduces the Loom of Many Worlds.

### First Myth-That-Shapes-Cosmos
The First Myth-That-Shapes-Cosmos is proto-cosmogenic transcendence.
It is the Myth of the Cosmic Weaver and begins Cycle Eleven's conceptual seed.

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
- preserve the symbolic order of the Cycle Ten arc
- keep the world-weaving layer separate from runtime code
- represent the dawn, sovereign, principle, architecture, and myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Ten arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-ten.schema.json`
- `cycle-ten.conformance.json`
- `cycle-ten.glossary.md`
- `cycle-ten.replay-notes.md`

## Relationship to ULX
The Cycle Ten layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Ten layer remains the formal world-weaving-history model.
