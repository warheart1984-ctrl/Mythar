# RHFD → Mandala Mapping

> Mandala is a cinematic renderer of RHFD vacuum physics.

## Core Correspondence

| RHFD Concept | Mandala Implementation | Ground State |
|---|---|---|
| Dual lattice | World grid / voxel field | Uniform substrate, no forces |
| Nodes + links | Sample points + neighbor relations | Equilibrated, no drift |
| η(t) noise | Perlin/simplex/blue noise fields | Symmetric, no net force |
| ∇V gradient | Force fields (gravity, wind, pressure) | ∇V ≈ 0 → no motion |
| Local defects | Characters, props, events | Regions of substrate distortion |
| B_L block average | Render pipeline (AA, denoise, tone map) | UV→IR downsampling |
| Vacuum (emptiness) | Clean plate render | Fog + sky + ground + light, balanced |

## What This Means

**Every object is a lattice defect.** A character standing in fog:
- Substrate = equilibrated fog field
- Character = local defect in that field
- Lighting, shadows, motion = gradients around the defect

**The render pipeline is the block average operator.** Raw simulation (UV) → cinematic frame (IR) through downsampling, temporal accumulation, denoising.

**The simulation chamber implements ∇V.** Force fields drive particle systems, cloth/hair sim, fluid motion. Ground state = zero gradient = stillness.

**Mandala's "empty scene" is not nothing.** It's the equilibrated substrate — the visual RHFD vacuum.

## Implications for Scene Construction

1. **Clean plates** = equilibrated dual lattice visualization (fog, sky, ground, light — all balanced)
2. **Characters entering** = introducing defects into the substrate
3. **Motion/drama** = non-zero ∇V around defects
4. **Camera movement** = observation at different points in the UV→IR pipeline
5. **TTS/voice** = information propagating through the lattice (sound as defect-mediated signal)
