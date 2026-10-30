# Community Scripts and Kubernetes

Community Scripts installs applications into Proxmox LXC containers and virtual machines. Kubernetes manages containerized workloads. A recipe's presence in the Community Scripts catalog does not establish that the same application has a maintained Kubernetes deployment.

The scanner reports syntax, shared Core entry points, potential prompts, retirement markers, and selected VM field references. It does not test Kubernetes images or charts.

## Choosing a deployment

| Question | Proxmox guest | Kubernetes workload |
| --- | --- | --- |
| What is installed? | Application script inside an LXC or VM | Container images managed by Kubernetes resources |
| Where is application state stored? | Guest filesystem or attached storage | Persistent volumes, external services, or ephemeral storage |
| What handles upgrades? | Guest-specific installer or updater | Image or chart changes followed by workload reconciliation |
| What provides guest services? | Proxmox guest and host configuration | Kubernetes networking, storage, identity, and scheduling |

These are differences in deployment mechanism, not measured advantages. Compare requirements for a particular application before selecting either option.

## Checking a Kubernetes alternative

For each application, establish the upstream application's maintained container images or supported deployment instructions. Where a Helm chart or operator exists, record its repository, version, maintainer, and supported application version. Documentation for a chart does not establish that it installs the same configuration as a Community Scripts recipe.

Check the source for requirements that may change the deployment: device access, privileged operations, host networking, fixed service ports, external databases, host paths, persistent files, backups, identity, and update procedures. The current source scanner does not verify all of these requirements. An absent match means *unknown*, not *unnecessary*.

Treat migration as an application-specific operation. Export or back up the data from the existing guest, create the replacement service, restore the data using the application's documented method, and test it before changing clients or ingress. Moving a guest filesystem into a Kubernetes volume is not a general migration procedure.

## What belongs in this repository

A useful extension would be a **curated deployment-options index** linking a recipe slug to verified upstream application documentation, container image sources, and Helm or operator documentation. Each entry should identify who verified the link and at which source revision. Missing entries should be reported as unknown.

Avoid generating Kubernetes manifests from shell-installation settings. There is no general translation from Proxmox guest properties, `var_*` or `VM_*` installer variables to Kubernetes Pods, security contexts, storage classes, or Services.

## Scope of current results

The `recipes.json` index contains static Proxmox script evidence, not Kubernetes readiness or app-version parity. Terraform and Ansible can continue to use that evidence for read-only review and independently check their pinned installers. Kubernetes installation, cluster inventory, and release validation would need separate implementations and tests.
