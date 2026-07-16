# Mythar Core v0.1

A dependency-free reference compiler for the Mythar Constitutional Registry v0.1.

## Run

```powershell
cd G:\mythar-core
python -m mythar compile "ja tor"
python -m mythar test
```

The compiler loads `G:\mythar-registry\registry-v0.1.json` by default. Override it with `--registry <path>` when embedding a different constitutional profile.

## Output

`compile` emits JSON containing a semantic DAG, meaning object, lineage, frame, reduction trace, and diagnostics. It is intentionally deterministic: it validates declared constitutional rules and does not claim an authoritative English translation.
