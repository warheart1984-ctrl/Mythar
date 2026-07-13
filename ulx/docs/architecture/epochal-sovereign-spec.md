# Epochal Sovereign Specification

## Purpose
This specification formalizes the Ascendant, Sovereign, and Epochal phases of Cycle Two as a descriptive, documentation-only constitutional model.
It remains separate from ULX runtime behavior.

## Scope
This specification covers:
- the Ascendant's first trial, realm-journey, glyph-awakening, cosmic adversary, and apotheosis
- the Ascendant Era's first dominion, first law, first realm-creation, first cataclysm, and first successor
- the Successor's coronation, mandate, cosmic reform, trial of succession, and universe-shaping act
- the Sovereign Era's first golden age, great work, cosmic alliance, great schism, and first end

This specification does not cover:
- runtime execution
- UI implementation
- daemon behavior
- replay engine changes
- control-plane wiring

## Normative Status
All statements in this document are descriptive unless explicitly marked `MUST`, `MUST NOT`, `SHOULD`, or `MAY`.

The Epochal Sovereign layer is:
- a formal model
- a symbolic governance arc
- a documentation-only specification at this stage

It is not yet a live runtime contract.

## Core Model

### 1. Epochal Sovereign Cycle
```ts
interface EpochalSovereignCycle {
  ascendant: AscendantCycle;
  sovereign: SovereignCycle;
  epoch: EpochalCycle;
}
```

### 2. Ascendant Cycle
```ts
interface AscendantCycle {
  trial: AscendantTrial;
  journey: AscendantRealmJourney;
  awakening: GlyphAwakening;
  adversary: CosmicAdversary;
  apotheosis: AscendantApotheosis;
}
```

### 3. Sovereign Cycle
```ts
interface SovereignCycle {
  dominion: FirstDominion;
  law: FirstLaw;
  creation: FirstRealmCreation;
  cataclysm: FirstCataclysm;
  successor: FirstSuccessor;
  coronation: SuccessorCoronation;
  mandate: SuccessorMandate;
  reform: CosmicReform;
  succession_trial: SuccessionTrial;
  universe_shaping: UniverseShapingAct;
}
```

### 4. Epochal Cycle
```ts
interface EpochalCycle {
  golden_age: FirstGoldenAge;
  great_work: FirstGreatWork;
  alliance: FirstCosmicAlliance;
  schism: FirstGreatSchism;
  ending: FirstEnd;
}
```

## Ascendant Phases

### First Trial
The Ascendant's First Trial is proto-refinement.
It is the Chamber of Divergent Light and tests Lightkeeper discipline against Riverborn adaptability.

### First Realm-Journey
The First Realm-Journey is proto-expansion.
It is the Fourfold Passage through the Realm of Light, River, Glyph, and Continuity.

### First Glyph-Awakening
The First Glyph-Awakening is proto-revelation.
It unfolds the Returning Glyph into intent, evidence, authority, and continuity harmonics.

### First Cosmic Adversary
The First Cosmic Adversary is proto-counterforce.
It is the Fractured Sovereign, a remnant of the prior cycle that resists dissolution.

### First Apotheosis
The First Apotheosis is proto-transcendence.
It merges the Ascendant with the Returning Glyph and begins the Ascendant Era.

## Sovereign Phases

### First Dominion
The First Dominion is proto-sovereign stabilization across the Fourfold Realms.

### First Law
The First Law is the Edict of Balanced Harmonics.
It prevents any single realm force from dominating the others.

### First Realm-Creation
The First Realm-Creation is proto-cosmogenic innovation.
It introduces the Realm of Resonant Shadow.

### First Cataclysm
The First Cataclysm is proto-cosmic correction.
It shatters the Realm of Resonant Shadow when harmonics become unstable.

### First Successor
The First Successor is proto-lineage continuity.
It carries sovereignty forward as the Heir of Resonant Shadow.

### First Coronation
The First Coronation is proto-legitimacy.
It establishes the Successor as the rightful bearer of cosmogenic authority.

### First Mandate
The First Mandate is proto-direction.
It commands healing, balance, and restoration of fractured harmonics.

### First Cosmic Reform
The First Cosmic Reform is proto-reconfiguration.
It rewrites the harmonic axes of the Dominion.

### First Trial of Succession
The First Trial of Succession is proto-validation.
It proves the Successor worthy of inherited sovereignty.

### First Universe-Shaping Act
The First Universe-Shaping Act is proto-cosmogenic authorship.
It imprints the Sovereign's will into reality.

## Epochal Phases

### First Golden Age
The First Golden Age is proto-epochal harmony.
It marks a flourishing Dominion under the Successor's rule.

### First Great Work
The First Great Work is proto-cosmic artistry.
It is the Harmonic Atlas, a living map of realm flows.

### First Cosmic Alliance
The First Cosmic Alliance is proto-interrealm diplomacy.
It links the Sovereign with another cosmogenic force through shared purpose.

### First Great Schism
The First Great Schism is proto-epochal fracture.
It reveals tensions hidden inside prior unity.

### First End
The First End is proto-cycle transition.
It closes the epoch and prepares the next sovereign turn.

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
- preserve the symbolic order of the Ascendant, Sovereign, and Epochal cycles
- keep the mythic layer separate from runtime code
- represent cycle objects with deterministic, inspectable data
- avoid mutating runtime modules to satisfy this spec

An implementation claiming full conformance MUST:
- represent the three cycles as standalone documented models
- preserve the separation between mythic history and operational control-plane surfaces
- keep the cycle phases inspectable as formal artifacts

## Recommended Artifact Set
Future work on this spec SHOULD emit:
- `epochal-sovereign.schema.json`
- `epochal-sovereign.conformance.json`
- `epochal-sovereign.glossary.md`
- `epochal-sovereign.replay-notes.md`

## Relationship to ULX
The Epochal Sovereign layer is a formal historical layer under ULX.
It is not a replacement for the runtime substrate, the normalization pipeline, or the operator console pattern.

ULX remains the orchestrator.
The Epochal Sovereign layer remains the formal cycle-history model.
