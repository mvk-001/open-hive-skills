# Repository Guidelines

## Project Structure & Module Organization
The repository is organized around reusable OpenClaw skills.

- `skills/<skill-name>/SKILL.md`: required skill definition (frontmatter + usage).
- `skills/<skill-name>/scripts/`: optional automation scripts.
- `skills/<skill-name>/assets/`: templates or static resources.
- `skills/<skill-name>/references/`: examples and supporting reference material.
- `docs/`: shared project documentation (for example `docs/youtube-radar/subscriptions-analysis.md`).

Use kebab-case for skill folders (example: `technical-report-pro`).

## Build, Test, and Development Commands
This repo does not use a single global build system; run commands from the relevant skill folder.

- `uv run skills/model-ranker/scripts/benchmark.py`: run model ranking sample.
- `python skills/openapi-integrator/scripts/openapi_to_skill.py <spec> --output skills/`: generate a skill from OpenAPI/Swagger.
- `python skills/technical-report-pro/scripts/report_gen.py --list`: list report templates.
- `python skills/technical-report-pro/scripts/report_gen.py --type arch-review --title "System Review"`: generate a report draft.

## Coding Style & Naming Conventions
- Language: English only (code, comments, docs, folder names).
- Python: target Python 3.13+ for new scripts.
- New Python scripts should use `uv`, `typer`, and inline dependency headers (`# /// script`).
- Naming: `snake_case` for Python identifiers, `kebab-case` for skill directories, clear descriptive filenames.
- Keep scripts small and composable; place reusable guidance in `SKILL.md`.

## Testing Guidelines
No centralized test suite is configured yet. Validate changes with focused script runs:

- Run each modified script with a realistic input.
- Verify generated artifacts (for example generated skill folders or report files).
- For parser/generator changes, include at least one URL input and one local file input in manual checks.

## Commit & Pull Request Guidelines
Follow the commit style visible in history: `type: short description` (examples: `docs: ...`, `feat: ...`, `security: ...`).

- Keep commits scoped to one logical change.
- PRs should include: purpose, impacted paths, verification commands, and sample output when generation behavior changes.
- Link related issues and include before/after snippets for documentation or template updates.
