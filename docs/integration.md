# Using recipe scan data

Terraform and Ansible can read `recipes.json` to find candidate recipes and show the reason for a static warning. The record includes an assessment, potential prompts, source URL and the two upstream revision hashes.

## Revision matching

Every report contains `scripts_revision` and `core_revision`. Consumers should compare **both** against the refs selected for an IaC operation before using a recorded assessment. Data from a different revision may describe another script implementation.

A matching revision makes the report relevant to the selected source. It does not establish successful execution or the safety of running the code as root.

## Displaying a warning

For a selected `kind` and `script`, look up `recipes["<kind>/<script>"]` and report the recorded category, prompt evidence and source URL. If the recipe is not present, if the revisions differ, or if no matching status file is available, report the absence of scan evidence.

Do not convert `shared_engine_no_app_prompts_detected` into a success or approval flag. Distinguish `retired`, `syntax_error`, and `custom_entrypoint` when explaining why a recipe needs review.

## Installation checks

The Terraform provider reads selected pinned source during planning. The Ansible collection checks script identity and Proxmox configuration when managing a guest. Both enforce their own execution approvals and operate independently of the common repository.

Recipe status is advisory. It does not replace selected-source inspection, configuration validation, guest identity checks, or host-side installation controls. No shared IaC parameter definitions or Python package dependency are required.

## Versioning

`recipes.json` has `format_version: 1` and `validation: static_only`. Consumers should reject unknown format versions and treat absent evidence as unknown, not success. Static report contents may change as detectors are improved; comparing reports from two scanner revisions may reflect detection changes as well as changes to upstream source.
