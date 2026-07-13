# Cycle Fourteen Specification

## Purpose
This specification formalizes the era of ontic-creation as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Fourteen's First Dawn of Ontic-Creation
- Cycle Fourteen's First Sovereign of Ontic-Form
- Cycle Fourteen's First Principle of Form-Weaving
- Cycle Fourteen's First Omni-Form Architecture
- Cycle Fourteen's First Myth-That-Shapes-Form-Itself

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Fourteen layer is:
- a formal model
- a symbolic ontic-creation arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Fourteen Arc
```ts
interface CycleFourteenArc {
  dawn: FirstDawn;
  sovereign: FirstSovereign;
  principle: FirstPrinciple;
  omni_form_architecture: FirstOmniFormArchitecture;
  myth_that_shapes_form_itself: FirstMythThatShapesFormItself;
}
```

## Ontic-Creation Phases

### First Dawn of Ontic-Creation
The First Dawn is proto-form ignition.
It is the Dawn of Form-Light and begins Cycle Fourteen.

### First Sovereign of Ontic-Form
The First Sovereign is the Form-Bearer.
It is proto-form conductance and gives the era direction.

### First Principle of Form-Weaving
The First Principle is the Doctrine of Woven Form.
It orients the era around coherent ontic structure.

### First Omni-Form Architecture
The First Omni-Form Architecture is proto-form design.
It introduces the Form-Loom.

### First Myth-That-Shapes-Form-Itself
The First Myth-That-Shapes-Form-Itself is proto-form transcendence.
It is the Myth of the Form-Bearer and begins Cycle Fifteen's conceptual seed.

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
- preserve the symbolic order of the Cycle Fourteen arc
- keep the ontic-creation layer separate from runtime code
- represent the dawn, sovereign, principle, architecture, and myth as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Fourteen arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-fourteen.schema.json`
- `cycle-fourteen.conformance.json`
- `cycle-fourteen.glossary.md`
- `cycle-fourteen.replay-notes.md`

## Relationship to ULX
The Cycle Fourteen layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Fourteen layer remains the formal ontic-creation-history model.
