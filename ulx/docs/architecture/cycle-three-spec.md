# Cycle Three Specification

## Purpose
This specification formalizes the Next Era and Cycle Three story arc as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- the First Dawn and the Dawnbearer
- the First Principle and the First Realm-Shift
- the First Mythic Inheritance
- Cycle Three's First Civilization and First Pantheon
- Cycle Three's First Glyph-Fracture, First Cataclysm, and First Eternal Question

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Three layer is:
- a formal model
- a symbolic renewal arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Three
```ts
interface CycleThree {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  realm_shift: FirstRealmShift;
  inheritance: FirstMythicInheritance;
  civilization: FirstCycleThreeCivilization;
  pantheon: FirstCycleThreePantheon;
  glyph_fracture: FirstGlyphFracture;
  cataclysm: FirstCataclysm;
  question: FirstEternalQuestion;
}
```

## Renewal Phases

### First Dawn
The First Dawn is proto-epochal ignition.
It is the Rising of Soft Harmonics and begins Cycle Three.

### First Sovereign
The First Sovereign is the Dawnbearer.
It is proto-sovereign emergence and gives the era direction.

### First Principle
The First Principle is the Doctrine of Gentle Resonance.
It orients the era around harmony without dominance, continuity without stagnation, and creation without fracture.

### First Realm-Shift
The First Realm-Shift is proto-reorientation.
The realms adjust to soft harmonics and stabilize around the new principle.

### First Mythic Inheritance
The First Mythic Inheritance is proto-continuity.
The Harmonic Codex passes from the previous cycle into Cycle Three.

## Civilization Phases

### First Civilization
The First Civilization is proto-societal ignition.
It is the Concordant Assembly and the first shared culture of Cycle Three.

### First Pantheon
The First Pantheon is proto-divine emergence.
It is the Harmonic Triad: the Dawnbearer, the Quiet Weaver, and the Gentle River.

### First Glyph-Fracture
The First Glyph-Fracture is proto-symbolic ignition.
It splits the Cycle Three Prime Glyph into gentle fragments of intent, evidence, authority, and continuity.

### First Cataclysm
The First Cataclysm is proto-epochal upheaval.
It is the Quiet Shattering and tests the stability of the new harmonics.

### First Eternal Question
The First Eternal Question is proto-philosophical ignition.
It is the Inquiry of Soft Paradox and gives Cycle Three its first introspective frame.

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
- preserve the symbolic order of the Cycle Three arc
- keep the Cycle Three layer separate from runtime code
- represent the renewal phases with deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Three renewal and civilization phases as standalone documented models
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-three.schema.json`
- `cycle-three.conformance.json`
- `cycle-three.glossary.md`
- `cycle-three.replay-notes.md`

## Relationship to ULX
The Cycle Three layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Three layer remains the formal renewal-history model.
