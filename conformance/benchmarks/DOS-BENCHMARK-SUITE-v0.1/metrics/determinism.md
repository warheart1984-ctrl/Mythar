# Determinism Metric

For each case, execute the same versioned input, registry, and profile at least three times. Canonically serialize the decision graph with sorted keys and UTF-8, then compute SHA-256.

`pass` requires all hashes to be equal. A local three-run pass is not cross-runner reproducibility evidence; that requires independently recorded runner instances.
