# MCP Mastery Research Summary

| Field | Value |
| --- | --- |
| Title | MCP Integration Mastery: Guardrails and Context Injection |
| Date | 2026-02-05 |
| Version | 1.0 |
| Intelligence Engine | Codex (GPT-5) |
| Risk Level | Medium |
| Immutable Reference | SHA256(mcp_meth_notes.json): 3e7266b0c7aae81ae8ccd5a3327ba801fb50c53ec9882a0181ad4b46f5ff450b |

## Problem Statement
We need to extract the core methodology from arXiv:2601.23049 (MedMCP-Calc) and apply it to harden MCP tool usage, reducing tool-call hallucinations and execution errors in our MCP-based skills.

## Methodology
- Sources: internal paper summary list and monthly scan data (no full paper text available in repo).
- Tools: CLI file inspection, local synthesis.
- Analytical framework: benchmark inference from title + key innovations, then map to guardrail system design.

## Scenario Analysis
1. **Low Latency, Small Tool Set**
   - Context pack injects 8 tools.
   - Expect stable selection and low token cost.
2. **High Tool Count, Token Pressure**
   - Tool index only, then progressive disclosure.
   - Expect reduced context overflow and fewer tool misfires.
3. **Failure Scenario: Schema Drift**
   - Tool schema changes but index is stale.
   - Guardrail scripts detect missing schema fields and halt before unsafe calls.

## Technical Justification
- The benchmark title implies evaluation of realistic medical calculator workflows under MCP integration; these flows are sensitive to schema errors and incorrect tool selection.
- Tool-call hallucinations are often caused by excessive context injection and ambiguous tool catalogs.
- A context pack + progressive disclosure approach reduces exposure, while linting enforces schema correctness before tool calls.

## Implementation Details
- New skill: `skills/mcp-mastery/SKILL.md`
- Guardrail scripts:
  - `skills/mcp-mastery/scripts/build_mcp_context.py`
  - `skills/mcp-mastery/scripts/mcp_tool_lint.py`
- New protocol: `docs/protocols/ARCHIE-ENG-002-MCP-INTERACTION.md`

## Proposed MCP Benchmark Methodology (Inferred)
Based on the title and internal key-innovation hints (no abstract available), the benchmark likely:
- Uses realistic medical calculator tasks (dose, risk, or score calculators) mapped to tool calls.
- Measures tool selection accuracy, schema correctness, and end-to-end task completion.
- Evaluates performance under varying tool-set sizes to stress context injection strategies.
Note: the internal scan mentions \"Mixture-of-Planners (MCP)\" which may be a naming mismatch with Model Context Protocol. This analysis focuses on MCP as Model Context Protocol because of the paper title and local MCP architecture context.

## Guardrail Recommendations
- Progressive disclosure of tool schemas.
- Deterministic tool filtering before model selection.
- Selection justification required before calls.
- Post-call schema validation and payload filtering.

## Performance Guardrails
- Latency budget: 4 seconds end-to-end for context injection + first tool call.
- Token budget: 2,000 tokens for tool index + selected schemas.
- Breach handling: reduce tool details to top 5 and require explicit user confirmation.

## Strategic Recommendation
**Go**: adopt the MCP mastery guardrails and ARCHIE-ENG-002 standards. The expected gains are fewer tool-call hallucinations and lower token cost without requiring MCP server changes.

## Proof of Concept / Verification
- `python3 -m py_compile skills/mcp-mastery/scripts/build_mcp_context.py`
- `python3 -m py_compile skills/mcp-mastery/scripts/mcp_tool_lint.py`
Result: both commands completed with exit code 0.

## Checklist (ARCHIE-ENG-001)
- [x] Language: Strictly English.
- [x] Format: Valid Markdown.
- [x] Integrity: All claims grounded in repo sources or explicitly inferred.
- [x] Scenarios: Includes failure scenario.
- [x] Performance Guardrails: Budgets declared with breach handling.
- [x] Version Control: Immutable reference recorded.
- [x] Attachments: Raw data in `research/2026-02-05/mcp_meth_notes.json`.
