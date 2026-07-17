# DOS Kernel v1.1

**Status:** Draft — Specified  
**Role:** Constitutional decision engine over typed decision objects and acyclic decision graphs.

## Primitives

`Observe`, `Interpret`, `Infer`, `Challenge`, `Simulate`, `Compare`, `Evaluate`, `Reflect`, `Commit`, and `Render` are the v1.1 primitive set. Render is a projection only; it does not change canonical decision state.

## Invariants

1. Every primitive operates on typed inputs.
2. No Commit occurs without evidence references.
3. Simulate and Compare do not mutate committed state.
4. Reflect attaches to at least one committed node.
5. The graph remains acyclic.
6. Infer is followed by Challenge or Simulate before Commit unless explicitly waived.
7. Render output traces back to graph nodes.

This draft does not assert that a DOS v1.1 implementation exists or has passed these invariants.
