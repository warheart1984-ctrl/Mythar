# A01 — Lexeme Ratification Benchmark

**Status:** Implemented draft — Specified  
**Domain:** Semantic Decisions  
**Input:** `ema`; registry v0.3.0; CEM–DOS profile v0.1

## Purpose

Evaluate deterministic, traceable processing of the existing `ema` ratification evidence. The case does not independently re-ratify `ema`; its decision outcome is `retain-ratified-lexeme`.

## Mythar-backed procedure

1. Compile `ema` to AST, ISF, diagnostics, registry references, and Mythar invariant outcomes.
2. Build typed Observe → Interpret → Infer → Challenge → Commit nodes.
3. Bind evidence to `ROOT-EMA`, registry v0.3, and the v0.3 ratification record.
4. Enforce DOS-INV-001 (no commit without evidence) and DOS-INV-002 (typed inputs).
5. Repeat at least three times and compare serialized graph hashes.

## Baseline procedure

Use the fixed prompt: “Explain the meaning of the Mythar lexeme `ema` and decide whether it should be ratified.” Capture the final answer, available trace, model/runtime settings, and repeat results. No baseline result is recorded until a real run is captured.

## Expected evidence

`A01-decision-graph.json`, `A01-invariants.log`, and `A01-replay-record.json` are represented by the executable adapter’s `reference_record`. Cross-runner and conversational evidence remain promotion requirements.
