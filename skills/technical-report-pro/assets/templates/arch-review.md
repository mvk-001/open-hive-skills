# Architecture Review: {{TITLE}}

**Report ID**: ARCH-{{DATE}}-{{SEQ}}
**Author**: {{AUTHOR}}
**Date**: {{DATE}}
**Status**: {{STATUS}}

---

## Executive Summary

{{EXECUTIVE_SUMMARY}}

---

## 1. System Overview

### 1.1 Purpose
{{PURPOSE}}

### 1.2 Scope
{{SCOPE}}

### 1.3 Key Stakeholders
| Role | Name/Team | Interest |
|------|-----------|----------|
| {{STAKEHOLDER_ROLE}} | {{STAKEHOLDER_NAME}} | {{STAKEHOLDER_INTEREST}} |

---

## 2. Architecture

### 2.1 High-Level Diagram

```
{{ARCHITECTURE_DIAGRAM}}
```

### 2.2 Components

| Component | Responsibility | Technology | Location |
|-----------|----------------|------------|----------|
| {{COMPONENT_NAME}} | {{COMPONENT_RESP}} | {{COMPONENT_TECH}} | {{COMPONENT_LOC}} |

### 2.3 Data Flows

{{DATA_FLOWS}}

### 2.4 External Dependencies

| Dependency | Type | Purpose | Risk Level |
|------------|------|---------|------------|
| {{DEP_NAME}} | {{DEP_TYPE}} | {{DEP_PURPOSE}} | {{DEP_RISK}} |

---

## 3. Technical Justification

### 3.1 Design Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| {{DECISION}} | {{RATIONALE}} | {{ALTERNATIVES}} |

### 3.2 Trade-offs

{{TRADEOFFS}}

### 3.3 Constraints

- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}

---

## 4. Implementation Details

### 4.1 Key Files

| File | Purpose |
|------|---------|
| `{{FILE_PATH}}` | {{FILE_PURPOSE}} |

### 4.2 Configuration

```yaml
{{CONFIGURATION}}
```

### 4.3 Integration Points

{{INTEGRATION_POINTS}}

---

## 5. Verification

### 5.1 Test Results

```
{{TEST_OUTPUT}}
```

### 5.2 Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| {{METRIC_NAME}} | {{METRIC_VALUE}} | {{METRIC_TARGET}} | {{METRIC_STATUS}} |

---

## 6. Recommendations

### 6.1 Improvements
1. {{IMPROVEMENT_1}}
2. {{IMPROVEMENT_2}}

### 6.2 Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {{RISK_DESC}} | {{RISK_LIKELIHOOD}} | {{RISK_IMPACT}} | {{RISK_MITIGATION}} |

### 6.3 Next Steps
- [ ] {{NEXT_STEP_1}}
- [ ] {{NEXT_STEP_2}}

---

## Appendix

### A. Glossary
| Term | Definition |
|------|------------|
| {{TERM}} | {{DEFINITION}} |

### B. References
- {{REFERENCE}}
