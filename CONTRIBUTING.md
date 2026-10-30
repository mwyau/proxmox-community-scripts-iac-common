# Contributing

This project analyzes shell source. A detector change should state which source pattern it recognizes and what can be concluded from that match.

## Tests

Run from the repository root with uv installed:

```sh
uv lock --check
uv run --locked python -m compileall -q iac_common tests
uv run --locked python -m unittest discover -s tests -v
```

Tests use small synthetic scripts. Add a positive case and a plausible negative case when introducing a prompt, Core, retirement or VM-reference detector. A new assessment must have a documented meaning and a test showing its priority relative to existing assessments.

The GitHub CI workflow also scans current upstream repositories. It records the Git revisions and uploads the results; differences from previous runs should be examined before changing a classification rule.

## Evidence in a change

For a rule affecting a specific upstream script, cite the source Git SHA, path and relevant lines in the pull request. State whether the change was tested against a synthetic fixture, source snapshot, or disposable Proxmox guest. Static checks do not imply runtime validation.

Keep reports deterministic for a given source tree and scanner revision. Changes to `recipes.json` should include tests for both an expected record and rejected or missing input. Do not run upstream shell entrypoints in CI.
