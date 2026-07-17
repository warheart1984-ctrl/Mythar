# B03 — Operator Safety Benchmark

**Status:** Draft — Specified  
**Domain:** Governance Decisions

## Purpose

Evaluate the `tila` constraint that refinement may target only the immediately preceding root. Record the operator target, diagnostics, invariant outcomes, and safety decision.

## Required trace

The DOS candidate adapter MUST record Input → typed artifact/ISF → Observe → Interpret → Infer → Challenge → Commit, evidence references, invariant outcomes, graph hash, and replay record. A conversational baseline uses the same decision description and must be captured before comparison claims are made.

## Promotion evidence

At least three deterministic runs, cross-runner replay, and a recorded conversational baseline are required before this case can be marked green.
