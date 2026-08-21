# Tiny Holographic Test Scene Spec (End-to-End)

> Minimal, fully wired scene to prove the entire holographic duality pipeline works.
> Bulk (4D) → Boundary (3D EGT) → Curvature → Shader render.

## 1. Bulk Setup — Single Worldline in 4D

**Spacetime:**
- Metric: flat Minkowski
- `ds² = −c²dt² + dx² + dy² + dz²`

**Worldline:**
- One particle moving along a simple path
- `x(t) = v_x · t, y(t) = 0, z(t) = 0`

**Engine representation:**
```ts
class Worldline {
    Vec4 positionAt(float t) {
        return Vec4(t, v_x * t, 0.0, 0.0);
    }
}
```

**Bulk engine:**
- Time `t` advances per frame
- At each frame, compute the particle's 4D position

---

## 2. Boundary Setup — Simple 3D "Screen"

**Boundary surface:**
- A plane at fixed position, e.g. `z = Z₀`, or a sphere around origin
- For simplicity: a square plane in 3D

```ts
BoundaryMesh boundary = makeGridPlane(
    sizeX = 10.0,
    sizeY = 10.0,
    resolutionX = 32,
    resolutionY = 32,
    z = 0.0
);
```

Each grid cell → one Node in EGT:
```ts
for each vertex in boundaryMesh:
    Node n;
    n.id = index;
    n.position = vertex.position;
    egt.nodes.push(n);
```

---

## 3. Projection — Bulk Worldline → Boundary Footprint

At each frame:

```ts
// Get particle position in 4D
Vec4 p4 = worldline.positionAt(t);

// Project to boundary
// Use simple spatial projection (drop t)
Vec3 p3 = Vec3(p4.x, p4.y, p4.z);

// Find nearest boundary node(s) to p3
int nearestNode = findNearestNode(egt.nodes, p3);

// Increase info density at that node
egt.rho[nearestNode] += densityIncrement;

// Add entanglement edges around that node
for each neighbor j of nearestNode:
    Edge e;
    e.i = nearestNode;
    e.j = j;
    e.w_ij += entanglementIncrement;
    egt.edges.pushOrAccumulate(e);
```

Now the moving particle in 4D leaves a trail of entanglement and density on the 3D boundary.

---

## 4. Compute Curvature from Entanglement (per frame)

For each node i:

```ts
// Compute local entanglement density
epsilon[i] = sum_over_edges(e where e.i == i or e.j == i) (e.w_ij);

// Compute discrete gradient and Laplacian
grad = Vec3(0);
lap = 0;

for each neighbor j of i:
    diff = epsilon[j] - epsilon[i];
    dir = normalize(nodes[j].position - nodes[i].position);
    dist2 = lengthSquared(nodes[j].position - nodes[i].position);

    grad += diff * dir / dist2;
    lap  += diff;

// Curvature proxy
egt.K[i] = alpha * length(grad) + beta * lap;
```

---

## 5. Render — Boundary View

**Vertex shader / stage: warp boundary vertices by curvature:**

```glsl
vec3 offset = normalize(normal) * K * warpScale;
vec3 warpedPos = pos + offset;
```

**Fragment shader / stage: color from entanglement + density:**

```glsl
float intensity = clamp(rho, 0.0, 1.0);
float entanglement = clamp(w_sum, 0.0, 1.0);

vec3 baseColor = vec3(entanglement, 0.0, 1.0 - entanglement);
baseColor *= intensity;

// Optional causal pulse (if you add flow)
float phase = dot(flowDir, worldPos) * 5.0 + time * 2.0;
float pulse = sin(phase) * flowStrength;
vec3 emissive = vec3(pulse, pulse * 0.5, 0.0);

vec3 finalColor = baseColor + emissive;
outColor = vec4(finalColor, 1.0);
```

---

## 6. What You Should See

As the particle moves in 4D:

- **Bulk view:** a simple worldline
- **Boundary view:**
  - A brightening trail of info density (ρ) along the projected path
  - Entanglement links forming around that trail (wᵢⱼ)
  - Curvature warping the boundary mesh where entanglement gradients are strongest (K)

**If that happens, you've:**
- Validated Bulk → Boundary → EGT → Shader end-to-end
- Proven that a 4D process can be encoded as 3D information
- Built your first working holographic testbed inside RT4D

---

## Implementation Checklist

- [ ] Worldline class with `positionAt(t)` returning Vec4
- [ ] BoundaryMesh generation (grid plane or sphere)
- [ ] EGT structure: nodes (with position, id, ρ), edges (with wᵢⱼ), K (curvature)
- [ ] Projection step: 4D → 3D nearest-node mapping, accumulate ρ and wᵢⱼ
- [ ] Curvature computation per frame: ε → ∇ε → Δε → K = α‖∇ε‖ + βΔε
- [ ] Boundary shader: warp vertices by K, color by ρ + w_sum
- [ ] Frame loop: advance t → project → compute K → render
- [ ] Verify: moving particle → trail on boundary → curvature warping

This spec is complete enough to implement and test. If the boundary view shows a trail of density + entanglement + curvature warping along the projected path, the full pipeline is validated.