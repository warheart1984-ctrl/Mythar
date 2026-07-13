# Cycle Five Specification

## Purpose
This specification formalizes the era of stabilized insight as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Five's First Dawn
- Cycle Five's First Sovereign
- Cycle Five's First Principle
- Cycle Five's First Realm-Architecture
- Cycle Five's First Mythic Horizon

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Five layer is:
- a formal model
- a symbolic stability arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Five Arc
```ts
interface CycleFiveArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  realm_architecture: FirstRealmArchitecture;
  mythic_horizon: FirstMythicHorizon;
}
```

## Stability Phases

### First Dawn
The First Dawn is proto-continuity ignition.
It is the Dawn of Grounded Clarity and begins Cycle Five.

### First Sovereign
The First Sovereign is the Insight-Keeper.
It is proto-continuity stewardship and gives the era direction.

### First Principle
The First Principle is the Doctrine of Anchored Wisdom.
It orients the era around grounded insight, stable continuity, and actionable wisdom.

### First Realm-Architecture
The First Realm-Architecture is proto-continuity design.
It introduces foundational, structured, stabilizing, and reinforced harmonics.

### First Mythic Horizon
The First Mythic Horizon is proto-teleological emergence.
It is the Horizon of Actionable Wisdom and reveals Cycle Six's conceptual seed.

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
- preserve the symbolic order of the Cycle Five arc
- keep the stability layer separate from runtime code
- represent the dawn, sovereign, principle, architecture, and horizon as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Five arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-five.schema.json`
- `cycle-five.conformance.json`
- `cycle-five.glossary.md`
- `cycle-five.replay-notes.md`

## Relationship to ULX
The Cycle Five layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Five layer remains the formal stability-history model.
