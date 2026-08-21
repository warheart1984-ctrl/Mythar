# 4D→3D Projection Operator: P: R¹,³ → R³

> Clean, explicit mapping respecting spacetime structure — no "dropping time."

## 1. 4D Spacetime Metric (Minkowski)

```
gμν = diag(−c², 1, 1, 1)
xμ = (t, x, y, z)
ds² = gμν dxμ dxν = −c²dt² + dx² + dy² + dz²
```

## 2. Naive Projection (Geometric Only)

```
P_naive(t, x, y, z) = (x, y, z)
```

Matrix form:
```
P_naive = [[0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]]
        acting on [t, x, y, z]ᵀ
```

⚠️ **Loses causality and time structure.** Fine for pure visualization but not for physics.

## 3. Induced 3D Metric on Spacelike Slice

Pick a constant-time slice t = t₀. On that slice:

```
ds²|_{t=t₀} = dx² + dy² + dz²
```

The induced 3D metric hij (i, j ∈ {x, y, z}):

```
hij = gij,   i, j ∈ {x, y, z}
```

In general curved spacetimes:

```
hij = gij − gi0 gj0 / g00
```

This projects the full 4D metric onto a 3D hypersurface orthogonal to the time direction.

## 4. Projection Operator with Chosen Normal

Pick a unit timelike vector nμ (the "observer" or normal to the boundary):

```
Constraint: gμν nμ nν = −1
```

The projection tensor onto the 3D space orthogonal to nμ:

```
hμν = gμν + nμ nν
```

This hμν is your 4D→3D projector at the level of the metric:

- Kills components along nμ (time direction)
- Keeps components tangent to the 3D "space" seen by that observer

For any 4D vector Vμ, its 3D projected part:

```
V_proj^μ = h^ν_μ V^ν
```

where h^ν_μ = gαμ hαν.

## 5. Concrete Operator: Flat Minkowski + Static Observer

If we stick to flat Minkowski and a static observer:

```
nμ = (1/c, 0, 0, 0)
```

then:

```
gμν = diag(−c², 1, 1, 1)
nμ = gμν nν = (−c, 0, 0, 0)
```

Compute hμν = gμν + nμ nν:

```
hμν = [[0, 0, 0, 0],
       [0, 1, 0, 0],
       [0, 0, 1, 0],
       [0, 0, 0, 1]]
```

The projector kills the time component and keeps the spatial ones — but now it's derived from the spacetime structure, not arbitrarily.

### Code Operator

**Input:** 4D vector (t, x, y, z)

**Projected 3D vector:** (x, y, z)

**Metric for distances:** use hij instead of gμν

```
project_4d_to_3d(V4) = (V.x, V.y, V.z)
project_metric_4d_to_3d(g) = hij (keep spatial indices [1,2,3][1,2,3])
```

## 6. Where to Go Next

Once you have:

- Projection tensor hμν
- Chosen normal nμ  
- 3D induced metric on the boundary

You can:

1. **Project fields (not just points)** — apply hμν to field vectors at each grid point

2. **Encode time as information** —
   - Entanglement entropy across the boundary
   - Causal ordering from the projection
   - Boundary correlation functions as "time"

3. **Build dual 3D representation of 4D spacetime scenes** —
   - Bulk geometry → boundary information
   - Worldlines → correlation chains
   - Causal cones → light-sheet constraints
   - Energy density → boundary operator expectation values

4. **Implement in Mandala RT4D** —
   - Compute hμν at each voxel in the simulation grid
   - Project 4D field data onto 3D boundary
   - Store boundary operators as entanglement tensors
   - Visualize the boundary as a "holographic screen"

This gives you a principled, structure-preserving 4D→3D projection that can serve as the foundation for holographic duality in your engine.

## Summary Table

| Concept | Formula | Purpose |
|---|---|---|
| 4D metric | gμν = diag(−c², 1, 1, 1) | Spacetime geometry |
| Naive projector | P_naive(t,x,y,z) = (x,y,z) | Geometric visualization only |
| Induced 3D metric | hij = gij − gi0gj0/g00 | Physics-preserving projection |
| Projection tensor | hμν = gμν + nμ nν | Observer-dependent 3D space |
| Vector projection | V_proj^μ = h^ν_μ V^ν | Project any 4D vector |
| Concrete operator | (t,x,y,z) → (x,y,z) | Flat Minkowski, static observer |