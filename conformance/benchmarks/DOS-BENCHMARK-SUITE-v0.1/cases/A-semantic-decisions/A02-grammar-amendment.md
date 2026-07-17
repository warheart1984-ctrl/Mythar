# A02 — Grammar Amendment Benchmark

**Status:** Draft — Specified  
**Domain:** Semantic Decisions

## Purpose

Evaluate a proposed experimental right-associative particle-stack amendment. The input is a GrammarRuleArtifact and the decision trace must record amendment impact, strict-mode boundary, and conformance impact. No amendment is approved by this benchmark; the outcome remains pending evidence.

## Required trace

The DOS candidate adapter MUST record Input → typed artifact/ISF → Observe → Interpret → Infer → Challenge → Commit, evidence references, invariant outcomes, graph hash, and replay record. A conversational baseline uses the same decision description and must be captured before comparison claims are made.

## Promotion evidence

At least three deterministic runs, cross-runner replay, and a recorded conversational baseline are required before this case can be marked green.
