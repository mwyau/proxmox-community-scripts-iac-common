# Recipe assessment method

The scanner reads shell scripts in `ProxmoxVE/ct`, `ProxmoxVE/vm` and available `install/*-install.sh` files. It reads selected functions in the separate upstream Core repository. Each report records the source Git revisions. The Python code does not source or run an installer; shell syntax is checked with `bash -n`.

## Measurements and checks

For each recipe, `iac_common.scan.analyze()` records:

- Whether `bash -n` accepts the entry script and, for LXC, its corresponding install payload if present.
- Whether the script references `core/build.func` (LXC) or `pve/vm-core.func` (VM) and its expected entry point.
- Whether the selected Core source contains the tested unattended entry-point markers.
- Locations of potential prompt calls, including `msg_menu`, `vm_dialog`, `whiptail`, `dialog`, `prompt_confirm`, `prompt_input` and selected `read` forms.
- Variables whose names match `var_*` or `VM_*`. For VM scripts, `vm_field_evidence` records references to working variables such as `RAM_SIZE` and `STORAGE`.
- Retirement notices in an exit-only script, including an apparent rename target when present.

The nearest recognized shell function is recorded with each prompt site. This is textual context, not a control-flow or data-flow analysis.

## Assessments

The scanner selects one assessment using the following order:

| Assessment | Evidence |
| --- | --- |
| `syntax_error` | `bash -n` failed for the entry script or an available LXC install payload |
| `retired` | Exit-only stub with an explicit retirement/rename notice and nonzero exit; no recognized creation lifecycle |
| `custom_entrypoint` | Expected shared engine or entry point is absent, or the specified Core revision lacks the tested unattended markers |
| `shared_engine_no_app_prompts_detected` | Shared engine and entry-point checks passed; no matching prompt call was found |
| `shared_engine_install_input_review` | One or more potential prompts occur outside the recognized update/wizard contexts |
| `shared_engine_wizard_prompt_review` | Prompt calls occur in recognized wizard contexts, and none were classified as installation/unknown |
| `shared_engine_update_prompts_only` | Matching prompts occur only in recognized update functions |

`retired` entries are listed under `excluded_retired` in `compatibility.json` by default. The status index merges active and retired entries into one `recipes` dictionary. The output classification is not an installability rating.

## Interpreting results

A passing shell syntax check does not check external commands, the downloaded application's behavior, or whether the script will complete.

A missing prompt match does not establish unattended behavior. Prompts may occur in sourced files, dynamically constructed commands, called utilities or runtime branches that the scanner does not model. A detected prompt may be unreachable during installation.

References to `VM_*` or working variables show that text was found, not that a selected input changes the deployed VM. A shared Core function does not prove that every VM script uses each override.

The checked Core revision and recipe revision both affect an assessment. Compare reports only with their exact SHA values visible; a change may be caused by either repository. Tests with disposable Proxmox guests are needed to establish actual installation behavior.

## Files

- `compatibility.json` contains every scanned entry and prompt-site evidence.
- `compatibility.md` summarizes categories and lists up to 150 non-retired entries.
- `recipes.json` indexes records by `lxc/<slug>` or `vm/<slug>`, with revision-qualified source URLs. It has `validation: static_only` and format version 1.
- `changes.json` and `changes.md`, when generated, compare recorded evidence between two status files. They do not compare source blobs.

The weekly workflow performs the same read-only analysis. It does not update the checkout, execute retrieved installers, or measure deployment success.
