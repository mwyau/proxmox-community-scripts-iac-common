# Usage guide

## Inspect a single recipe

Clone the upstream repositories as shown in the [README](../README.md). Use the exact commits recorded by those checkouts:

```sh
SCRIPTS_SHA=$(git -C upstream-scripts rev-parse HEAD)
CORE_SHA=$(git -C upstream-core rev-parse HEAD)
uv run --locked python -m iac_common.scan --source upstream-scripts --core upstream-core \
  --kind lxc --script adguard --scripts-rev "$SCRIPTS_SHA" \
  --core-rev "$CORE_SHA" --strict-syntax --output out
uv run --locked python -m iac_common.status --scan out/compatibility.json --output out/recipes.json
```

This reads `ct/adguard.sh`, its install payload if present, and the selected Core files. It does not install AdGuard or connect to Proxmox.

Inspect the result:

```sh
jq '.recipes["lxc/adguard"] | {
  assessment, flags, syntax_ok, prompt_sites, source_url
}' out/recipes.json
```

For a VM, use `--kind vm --script ubuntu-vm` and inspect `.recipes["vm/ubuntu-vm"].vm_field_evidence`. A field's presence in the source is not a deployment test.

## Scan a particular revision

Use an immutable upstream commit rather than a moving branch when reproducing an earlier result:

```sh
git -C upstream-scripts fetch --depth 1 origin <scripts-commit-sha>
git -C upstream-scripts checkout --detach FETCH_HEAD
git -C upstream-core fetch --depth 1 origin <core-commit-sha>
git -C upstream-core checkout --detach FETCH_HEAD
```

Then run the scanner using the two `git rev-parse HEAD` values. The `--scripts-rev` and `--core-rev` arguments label the report; compute them from the checkouts. The scanner does not independently verify that a manually supplied label matches the directory contents.

## Compare snapshots

Save the two `recipes.json` files produced from distinct pinned scans, then run:

```sh
uv run --locked python -m iac_common.compare \
  --before snapshots/previous/recipes.json \
  --after snapshots/current/recipes.json \
  --output out/changes.json --markdown out/changes.md
```

Read `changed` for differences in assessment, syntax, prompts, flags, retirement and selected VM evidence. The `added` and `removed` entries refer to recipe identities in the scans. For changes with the same assessment, inspect `changed_fields`. Even with no recorded changes, the source may have changed in ways the scanner does not detect.

## GitHub Actions artifacts

The [scan workflow](../.github/workflows/scan.yml) supports manual selection of a recipe, kind, and upstream refs. The weekly schedule runs from the repository's default branch once the workflow is merged. Download `recipe-status` from its completed workflow run. The `upstream-preview` artifact from feature-branch CI uses the same file formats.

Reports currently expire after 30 days. Store copies externally for comparisons across longer periods. The repository does not publish a live status endpoint.
