# Boundary‑Encoded Facial Rigs

> Turning the face into a high‑resolution holographic boundary where expressions are patterns of information, not just sliders.

## Core Representation

### Nodes: Facial Vertices
- brows, eyelids (upper/lower), lips (upper/lower), cheeks, nose, jaw
- Each vertex vᵢ stores:
  - ρᵢ: local expression tension/activation (smile, frown, squint, etc.)
  - Region tag: brow, eye, nose, mouth, cheek, jaw
  - Control influence: weights to high‑level facial controls (e.g. "smile", "anger", "surprise")

### Edges (Entanglement)
wᵢⱼ high where:
- Vertices share the same expression zone (e.g. nasolabial fold)
- Skin is tightly coupled (eyelid, lip edges)
- Underlying muscle fibers connect (zygomaticus, orbicularis oculi, frontalis)

## Expression as Boundary Pattern

Instead of "blendshape: Smile = 0.7", you do:

### Expression Signal → Boundary Fields

For a given expression (e.g. smile):
- Increase ρᵢ in mouth corners, cheeks, lower eyelids
- Strengthen wᵢⱼ along smile lines and cheek arcs
- Define flow direction from mouth corners toward eyes

### Rig Response

Facial bones and control points (jaw, cheeks, brows) read the boundary state:
- High ρ + structured w → cheeks lift, lips curve, eyes narrow

**Micro‑expressions** become small, localized changes in ρ and w, not extra shapes.

#### Smile Pattern
- ρ↑ in zygomaticus region, mouth corners, cheeks
- w↑ along nasolabial fold, cheek arcs
- Flow: mouth corners → eyes

#### Frown Pattern
- ρ↑ in corrugator supercilii (between brows)
- w↑ between brow vertices
- Flow: downward between brows

#### Surprise Pattern
- ρ↑ across frontalis (forehead)
- w↑ spread toward temples
- Flow: outward from center

## Deformation

### Local Displacement
- **Mouth corners:** pulled along flow direction
- **Cheeks:** bulge via normal offset proportional to ρ
- **Eyelids:** close/open via entanglement along lid edges

### Smoothing via Entanglement
- Neighboring vertices blend motion based on wᵢⱼ
- Expressions look organic, not segmented

---

## Result

A facial rig where **expression = information pattern on the boundary**, and the geometry follows. No blendshape zoo required — the face is a governed informational surface.