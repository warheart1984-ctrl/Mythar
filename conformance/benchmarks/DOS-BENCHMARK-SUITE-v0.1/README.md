# DOS Benchmark Suite v0.1 — Mythar Decision Traceability & Reproducibility

**Status:** Draft — Specified  
**Scope:** Evaluate a Mythar-backed decision-trace adapter against a separately measured conversational baseline.

## Constitutional position

The suite provides evidence for the CEM–DOS Integration Profile v0.1. It does not ratify DOS, claim cross-hardware replay before it is measured, or assert superiority over conversational reasoning without recorded baseline runs.

## Procedure

1. Compile source to AST, ISF, diagnostics, registry references, and invariant outcomes.
2. Build typed decision objects through Observe, Interpret, Infer, Challenge, and Commit.
3. Record decision graph, invariant outcomes, evidence references, replay record, and graph hash.
4. Run each DOS case at least three times; measure hash equality and path completeness.
5. Compare against a separately captured conversational baseline using the same decision prompt.

## Metrics

- **Determinism:** graph-hash equality across at least three runs.
- **Traceability:** input → AST → ISF → decision nodes → invariants → outcome.
- **Reproducibility:** replay across distinct runner instances.
- **Invariant adherence:** no commit without evidence; no decision node without typed input.

Run the implemented A01 reference adapter:

```powershell
cd mythar-v0.2
$env:PYTHONPATH = '.\src'
python -m mythar dos-benchmark --runs 3
```
