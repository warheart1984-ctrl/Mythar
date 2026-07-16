# Mythar Core v0.1

A dependency-free reference compiler for the Mythar Constitutional Registry v0.1.

## Run

```powershell
cd mythar-core
python -m mythar compile "ja tor"
python -m mythar test
```

The compiler resolves the adjacent `mythar-registry/registry-v0.1.json` by default. Set `MYTHAR_REGISTRY_PATH` or pass `--registry <path>` to use another profile.

## Output

`compile` emits JSON containing a semantic DAG, meaning object, lineage, frame, reduction trace, and diagnostics. It is intentionally deterministic: it validates declared constitutional rules and does not claim an authoritative English translation.
