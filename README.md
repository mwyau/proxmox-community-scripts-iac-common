# Proxmox Community Scripts IaC — Common

Read-only recipe discovery, retirement detection, syntax checks, prompt-call evidence, and generated recipe status for the companion Terraform provider and Ansible collection.

This repository is **not** a Terraform provider, an Ansible collection, or a shell installer. It contains no shared guest-setting contract, no Proxmox credentials, and no host mutation code.

## What it contains

- `iac_common/scan.py`: source-only scan of upstream `community-scripts/ProxmoxVE` and `community-scripts/core`
- `iac_common/retirement.py`: conservative retired/renamed stub detection
- `iac_common/catalog.py`: directory discovery and Git blob revision comparisons
- `iac_common/vm_evidence.py`: VM script variable-reference evidence (including bpg/proxmox-style setting names)
- `iac_common/status.py`: reproducible `recipes.json` status index keyed by `lxc/slug` or `vm/slug`

No installation scripts are executed. `bash -n` performs syntax checking only. Static detection of prompts or a shared Core entrypoint **does not establish safe unattended installation**. Every consumer must verify a selected pinned script and enforce its own execution approvals.

## Run locally

```sh
git clone --depth 1 https://github.com/community-scripts/ProxmoxVE.git upstream-scripts
git clone --depth 1 https://github.com/community-scripts/core.git upstream-core
SCRIPTS_SHA=$(git -C upstream-scripts rev-parse HEAD)
CORE_SHA=$(git -C upstream-core rev-parse HEAD)
python -m iac_common.scan --source upstream-scripts --core upstream-core \
  --scripts-rev "$SCRIPTS_SHA" --core-rev "$CORE_SHA" --output out --strict-syntax
python -m iac_common.status --scan out/compatibility.json --output out/recipes.json
python -m unittest discover -s tests -v
```

`out/recipes.json` includes the exact source revisions, per-recipe assessment, retirement, syntax and prompt evidence. `out/compatibility.md` is a human-readable summary. The GitHub workflow runs weekly or on demand and uploads the results as artifacts; **it does not automatically commit changing upstream output into the source branch**.

## Ownership

Source analysis moved from `mwyau/ansible-collection-proxmox-community-scripts`, and VM static field-use evidence also informs `mwyau/terraform-provider-proxmox-community-scripts` plan warnings. Terraform's pinned plan-time inspector and Ansible's catalog/provenance module remain self-contained for fail-closed runtime behavior. Do not install this package on Proxmox or depend on live network access to apply changes. Follow source SHA links in the report when investigating a recipe.

## Limits

The `shared_engine_no_app_prompts_detected` category is **not** a green light or guarantee; external app scripts, sourced functions, dynamically constructed commands, credentials and package downloads are not fully modeled. A recipe can change at any upstream revision. Never infer support for an unscanned commit.
