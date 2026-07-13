# Cycle Four Specification

## Purpose
This specification formalizes the era of wisdom as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Four's First Dawn
- Cycle Four's First Sovereign
- Cycle Four's First Paradox
- Cycle Four's First Realm-Architecture
- Cycle Four's First Mythic Purpose

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Four layer is:
- a formal model
- a symbolic wisdom arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Four Arc
```ts
interface CycleFourArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  paradox: FirstParadox;
  realm_architecture: FirstRealmArchitecture;
  mythic_purpose: FirstMythicPurpose;
}
```

## Wisdom Phases

### First Dawn
The First Dawn is proto-awareness.
It is the Emergence of Quiet Insight and begins Cycle Four.

### First Sovereign
The First Sovereign is the Wisdombearer.
It is proto-guiding consciousness and gives the era direction.

### First Paradox
The First Paradox is proto-philosophical ignition.
It is the Paradox of Knowing and Not-Knowing and deepens inquiry.

### First Realm-Architecture
The First Realm-Architecture is proto-metaphysical design.
It introduces layered light, recursive river, interpretive glyph, and branching continuity.

### First Mythic Purpose
The First Mythic Purpose is proto-teleological ignition.
It is the Purpose of Deepening Wisdom and gives Cycle Four its narrative direction.

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
- preserve the symbolic order of the Cycle Four arc
- keep the wisdom layer separate from runtime code
- represent the dawn, sovereign, paradox, architecture, and purpose as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Four arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-four.schema.json`
- `cycle-four.conformance.json`
- `cycle-four.glossary.md`
- `cycle-four.replay-notes.md`

## Relationship to ULX
The Cycle Four layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Four layer remains the formal wisdom-history model.
