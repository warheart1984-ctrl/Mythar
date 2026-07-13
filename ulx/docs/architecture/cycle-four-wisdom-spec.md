# Cycle Four Wisdom Specification

## Purpose
This specification formalizes the wisdom branch of Cycle Four as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- Cycle Four's First Civilization
- Cycle Four's First Glyph-Awakening
- Cycle Four's First Great Insight
- Cycle Four's First Cataclysm of Wisdom
- Cycle Four's First Bridge to Cycle Five

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Cycle Four Wisdom layer is:
- a formal model
- a symbolic wisdom arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Cycle Four Wisdom Arc
```ts
interface CycleFourWisdomArc {
  civilization: FirstCivilization;
  glyph_awakening: FirstGlyphAwakening;
  great_insight: FirstGreatInsight;
  cataclysm_of_wisdom: FirstCataclysmOfWisdom;
  bridge_to_cycle_five: FirstBridgeToCycleFive;
}
```

## Wisdom Phases

### First Civilization
The First Civilization is proto-societal awakening.
It is the Reflective Conclave and the first society of wisdom.

### First Glyph-Awakening
The First Glyph-Awakening is proto-semantic revelation.
It unfolds the Cycle Four Prime Glyph into layered meanings.

### First Great Insight
The First Great Insight is proto-philosophical crystallization.
It is the Insight of Echoing Wisdom and stabilizes the era's ethos.

### First Cataclysm of Wisdom
The First Cataclysm of Wisdom is proto-epochal upheaval.
It is the Collapse of Over-Reflection and exposes the cost of infinite recursion.

### First Bridge to Cycle Five
The First Bridge to Cycle Five is proto-cycle transition.
It is the Path of Stabilized Insight and carries wisdom forward without fracture.

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
- preserve the symbolic order of the Cycle Four wisdom arc
- keep the wisdom layer separate from runtime code
- represent the civilization, awakening, insight, cataclysm, and bridge as deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the Cycle Four wisdom arc as a standalone documented model
- preserve the separation between mythic history and operational control-plane surfaces
- keep the phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `cycle-four-wisdom.schema.json`
- `cycle-four-wisdom.conformance.json`
- `cycle-four-wisdom.glossary.md`
- `cycle-four-wisdom.replay-notes.md`

## Relationship to ULX
The Cycle Four Wisdom layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Cycle Four Wisdom layer remains the formal wisdom-history model.
