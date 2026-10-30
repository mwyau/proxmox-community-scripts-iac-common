# Proxmox Community Scripts IaC — Common

Analyze [Proxmox Community Scripts](https://github.com/community-scripts/ProxmoxVE) recipes without running them. The scanner checks shell syntax, shared Core entry points, potential interactive prompts and retirement notices. It records the results for each LXC and VM recipe at specified Git revisions.

The results describe **source evidence**. A recipe with no detected prompts may still require input or fail during installation.

## Run a scan

Install [uv](https://docs.astral.sh/uv/) and run `uv sync --locked` from this directory. The project has no third-party Python dependencies.

uv and Bash are required. uv installs Python 3.12 from `.python-version`. From the repository root:

```sh
git clone --depth 1 https://github.com/community-scripts/ProxmoxVE.git upstream-scripts
git clone --depth 1 https://github.com/community-scripts/core.git upstream-core
SCRIPTS_SHA=$(git -C upstream-scripts rev-parse HEAD)
CORE_SHA=$(git -C upstream-core rev-parse HEAD)

uv run --locked python -m iac_common.scan --source upstream-scripts --core upstream-core \
  --scripts-rev "$SCRIPTS_SHA" --core-rev "$CORE_SHA" \
  --strict-syntax --output out
uv run --locked python -m iac_common.status --scan out/compatibility.json --output out/recipes.json
```

The scan writes `compatibility.json`, `compatibility.md` and `recipes.json`. The status index contains source links and script/Core revisions. GitHub Actions runs the scan weekly from the default branch and supports manual runs. Reports are uploaded as workflow artifacts for 30 days; they are not published as persistent files.

## Documentation

- [Usage guide](docs/usage.md): reproduce a scan, inspect a recipe, compare snapshots
- [Assessment method](docs/method.md): what is checked, classification rules and limitations
- [Using scan data](docs/integration.md): advisory interpretation for Terraform and Ansible
- [Kubernetes deployment considerations](docs/kubernetes.md): compare guest installations with Kubernetes applications and their data requirements
- [Curated Kubernetes references](docs/kubernetes-alternatives.md): reviewed container images, Helm charts and operators for selected recipes
- [Contributing](CONTRIBUTING.md): tests and examples for detector changes

## Review Kubernetes deployment references

```sh
uv run --locked python -m iac_common.kubernetes list
uv run --locked python -m iac_common.kubernetes show lxc/gitea
uv run --locked python -m iac_common.kubernetes validate --recipes out/recipes.json
```

The curated index covers selected applications and records evidence links; `unknown` is used where a deployment option has not been reviewed. This does not establish Kubernetes compatibility or replace installation tests.

## Compare two scans

```sh
uv run --locked python -m iac_common.compare --before old/recipes.json --after new/recipes.json \
  --output out/changes.json --markdown out/changes.md
```

A comparison lists new or missing recipe names and changes in recorded evidence. It does not compare every line of source code. An unchanged assessment is not evidence that the upstream recipe is unchanged.

The companion [Terraform provider](https://github.com/mwyau/terraform-provider-proxmox-community-scripts) and [Ansible collection](https://github.com/mwyau/ansible-collection-proxmox-community-scripts) perform their own pinned-source and Proxmox checks before installation. Scan results do not authorize executing installer scripts as root.
