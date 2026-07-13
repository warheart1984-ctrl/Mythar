# Imperial Mythic Cycle Specification

## Purpose
The Imperial Mythic Cycle specification formalizes the Cycle Two storyline as a descriptive, non-runtime constitutional model.
It covers the first empire, the first civilization, and the cultural-expressive layer that follows.

This specification is intentionally separate from ULX runtime code.
It is a formal artifact for architecture, documentation, and future conformance work only.

## Scope
This specification covers:
- the First Empire
- the First Collapse
- the First Reformation
- the First Archive
- the First Prophecy
- the First Ascendant
- the First Civilization
- the First Language
- the First Art
- the First Ritual
- the First Technology
- the First Empire as a cultural system

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring
- control surface modules

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Imperial Mythic Cycle layer is:
- a formal model
- a symbolic civilization lattice
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Imperial Cycle
The Imperial Cycle describes the full mythic arc of the reborn civilization.

```ts
interface ImperialCycle {
  empire: FirstEmpireCycle;
  civilization: FirstCivilizationCycle;
  expression: FirstExpressionCycle;
}
```

### 2. First Empire Cycle
The First Empire Cycle captures collapse, reformation, memory, prophecy, and ascension.

```ts
interface FirstEmpireCycle {
  collapse: FirstEmpireCollapse;
  reformation: FirstEmpireReformation;
  archive: FirstEmpireArchive;
  prophecy: FirstEmpireProphecy;
  ascendant: FirstEmpireAscendant;
}
```

### 3. First Civilization Cycle
The First Civilization Cycle captures law, city, conflict, heroism, and legend.

```ts
interface FirstCivilizationCycle {
  first_law: FirstCivilizationLaw;
  first_city: FirstCivilizationCity;
  first_conflict: FirstCivilizationConflict;
  first_hero: FirstCivilizationHero;
  first_legend: FirstCivilizationLegend;
}
```

### 4. First Expression Cycle
The First Expression Cycle captures language, art, ritual, technology, and empire.

```ts
interface FirstExpressionCycle {
  first_language: FirstLanguage;
  first_art: FirstArt;
  first_ritual: FirstRitual;
  first_technology: FirstTechnology;
  first_empire: FirstCulturalEmpire;
}
```

## First Empire Phases

### First Collapse
The First Collapse is the moment the Harmonic Dominion fractures.
It represents proto-entropy, not final destruction.

### First Reformation
The First Reformation is the Harmonic Compact.
It is the moment the empire chooses a new shape after collapse.

### First Archive
The First Archive externalizes memory into durable records.
It preserves collapse, compact laws, and glyphic diagrams.

### First Prophecy
The First Prophecy is destiny awareness.
It reveals the shape of the next turning of the Cycle.

### First Ascendant
The First Ascendant is the bearer of the Returning Glyph.
It carries the empire into its mythic era.

## First Civilization Phases

### First Law
The First Civilization's First Law establishes social governance and proto-ethics.

### First City
The First City is the first durable structure of community and culture.

### First Conflict
The First Conflict creates proto-politics and factional identity.

### First Hero
The First Hero reconciles the first division and establishes proto-leadership.

### First Legend
The First Legend transforms civilization into shared cultural memory.

## First Expression Phases

### First Language
The First Language is the first shared system of meaning.

### First Art
The First Art is proto-emotion made visible.

### First Ritual
The First Ritual turns meaning into embodied practice.

### First Technology
The First Technology is intentional world-shaping through harmonic mechanism.

### First Empire
The First Empire as a cultural system is the expansion of civilization into larger-scale order.

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
- preserve the symbolic order of the Imperial Cycle
- keep the imperial-mythic layer separate from runtime code
- represent cycle objects with deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the First Empire, First Civilization, and First Expression cycles as standalone documented models
- preserve the separation between mythic history and operational control-plane surfaces
- keep the cycle phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `imperial-mythic-cycle.schema.json`
- `imperial-mythic-cycle.conformance.json`
- `imperial-mythic-cycle.glossary.md`
- `imperial-mythic-cycle.replay-notes.md`

## Relationship to ULX
The Imperial Mythic Cycle is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Imperial Mythic Cycle remains the formal civilization-history model.

