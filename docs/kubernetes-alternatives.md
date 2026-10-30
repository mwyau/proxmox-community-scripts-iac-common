# Curated Kubernetes deployment references

\`data/kubernetes-alternatives.json\` lists published container images, Helm charts, and operators for a small set of Proxmox Community Scripts applications. Each recipe name is checked against the Community Scripts source at a recorded Git revision. The links were reviewed on 2026-10-30.

The index is **not a compatibility assessment**. It does not test a Kubernetes cluster, install a chart, check current image tags, or prove that a guest can be migrated.

## Review the entries

Use [uv](https://docs.astral.sh/uv/) from the repository root:

\`\`\`sh
uv run --locked python -m iac_common.kubernetes list
uv run --locked python -m iac_common.kubernetes show lxc/immich
\`\`\`

The result includes the upstream application name, reviewed image and chart references, documentation links, publisher type, and specific migration considerations.

A \`null\` value for \`helm_charts\` or \`operators\` means **not verified**, not that no chart or operator exists. A chart marked \`community\` may be maintained by a community organization, including groups associated with the application. A chart marked \`application\` is linked from the application's own installation documentation. These labels indicate where documentation originates; they are not quality ratings.

A reference names the image repository or chart, **not a version or digest**. Before deploying, select a supported version, read the chart's current requirements and release notes, and verify it against the application release. For example, the Immich chart requires its own selected image tag and a database with the appropriate extension.

## Check the Proxmox recipe mapping

After generating a full \`out/recipes.json\` using the commands in the [README](../README.md), check the reviewed recipe names against that scan:

\`\`\`sh
uv run --locked python -m iac_common.kubernetes validate --recipes out/recipes.json
\`\`\`

Validation requires the same **scripts** revision and verifies that every curated \`kind/slug\` exists in the scan. It does not check external documentation URLs at runtime, compare Kubernetes and Proxmox installation results, or use the Core revision as a Kubernetes compatibility claim.

The curator can update entries for a newer script revision once the corresponding upstream scripts and external references have been reviewed. A modified link requires source evidence, not an inference from a script slug.

## Boundaries

Common Scripts can install a whole Linux guest with packages, system services, privileged files, devices, and network configuration. A Kubernetes chart may install several dependent workloads with different storage, security, and upgrade requirements. Check persistence, ingress, secrets, databases, root privileges, host networking and device access for each application. Home Assistant Container, for example, lacks the Supervisor apps available in Home Assistant OS.

The data serves as a discovery aid. It is not consumed by Terraform or Ansible to approve installation. No Kubernetes credentials or cluster mutation operations are used.

## Contributing entries

For each entry:

1. Confirm the exact Community Scripts \`ct/<slug>.sh\` or \`vm/<slug>.sh\` exists at the recorded source commit.
2. Link an application-maintained document for each image, Helm chart or operator. Label a chart from a separate maintained community repository as \`community\`.
3. Record requirements that affect equivalence, particularly data persistence and networking.
4. Use \`null\` where no reviewed reference is available. Do not assert that a deployment option is absent without checking.
5. Run \`uv run --locked python -m unittest discover -s tests -v\` and the \`validate\` command with the full pinned scan.

Treat the review date as the date when the cited documents were inspected. References may change after that date.
