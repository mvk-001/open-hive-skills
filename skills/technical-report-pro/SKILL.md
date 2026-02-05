---
name: technical-report-pro
description: Generate professional technical reports with strict structure. Use for architecture reviews, post-mortems, debug investigations, research summaries. Follows ARCHIE-ENG-001 protocol with Executive Summary, Technical Justification, Implementation Details, and Verification Proofs.
---

# Technical Report Pro

Generate professional, structured technical documentation following engineering best practices.

## Report Types

| Type | Template | Use Case |
|------|----------|----------|
| Architecture Review | `arch-review.md` | System design analysis, component relationships |
| Post-Mortem | `post-mortem.md` | Incident analysis, root cause, remediation |
| Research Summary | `research-summary.md` | Findings synthesis, recommendations |
| Debug Investigation | `debug-investigation.md` | Problem diagnosis, solution verification |

## Standard Structure (ARCHIE-ENG-001)

Every report MUST include:

### 1. Executive Summary (≤200 words)
- **What**: One-sentence description of the subject
- **Why**: Business/technical impact
- **Outcome**: Key findings or decisions
- **Action**: Next steps (if applicable)

### 2. Technical Justification ("The Why")
- Problem statement with context
- Constraints and requirements
- Alternative approaches considered
- Rationale for chosen approach

### 3. Implementation Details ("The How")
- Architecture diagrams (ASCII or Mermaid)
- Component breakdown
- Data flows
- Configuration details
- Code references (file paths, line numbers)

### 4. Verification Proofs ("The Evidence")
- Test results with actual output
- Metrics (before/after)
- Logs or command output
- Screenshots or recordings (paths)

## Usage

### Quick Generation

```bash
# Generate from template
python scripts/report_gen.py --type arch-review --title "OpenClaw Hive Architecture"

# With context gathering
python scripts/report_gen.py --type post-mortem --scan research/ --title "BlueBubbles Integration Issue"
```

### Template Selection

Choose template based on:

| Trigger | Template |
|---------|----------|
| "How does X work?" | arch-review |
| "What went wrong?" | post-mortem |
| "What did we learn?" | research-summary |
| "Why is X broken?" | debug-investigation |

## Writing Guidelines

1. **Language**: English only (per protocol)
2. **Tone**: Technical, precise, no fluff
3. **Evidence**: Every claim needs proof
4. **Brevity**: Prefer tables/lists over paragraphs
5. **Actionable**: End with clear next steps

## Context Gathering

Before writing, scan for context:

```bash
# Find relevant files
grep -r "keyword" research/ dev/ --include="*.md"

# Check recent work
ls -lt research/ | head -10

# Load memory
cat memory/observations.md | grep -i "topic"
```

## Templates

Templates are in `assets/templates/`. Load with:

```python
from pathlib import Path
template = Path("assets/templates/arch-review.md").read_text()
```

## Example Output

See `references/examples/` for sample reports demonstrating each template.
