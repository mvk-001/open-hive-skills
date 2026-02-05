# Post-Mortem: {{TITLE}}

**Report ID**: PM-{{DATE}}-{{SEQ}}
**Author**: {{AUTHOR}}
**Date**: {{DATE}}
**Severity**: {{SEVERITY}}
**Status**: {{STATUS}}

---

## Executive Summary

{{EXECUTIVE_SUMMARY}}

**Impact Duration**: {{DURATION}}
**Affected Systems**: {{AFFECTED_SYSTEMS}}
**Users Impacted**: {{USERS_IMPACTED}}

---

## 1. Incident Timeline

| Time (UTC) | Event | Actor |
|------------|-------|-------|
| {{TIME}} | {{EVENT}} | {{ACTOR}} |

---

## 2. Root Cause Analysis

### 2.1 What Happened
{{WHAT_HAPPENED}}

### 2.2 Why It Happened
{{WHY_IT_HAPPENED}}

### 2.3 Five Whys

1. **Why?** {{WHY_1}}
2. **Why?** {{WHY_2}}
3. **Why?** {{WHY_3}}
4. **Why?** {{WHY_4}}
5. **Why?** {{WHY_5}}

### 2.4 Contributing Factors
- {{FACTOR_1}}
- {{FACTOR_2}}

---

## 3. Detection & Response

### 3.1 How It Was Detected
{{DETECTION_METHOD}}

### 3.2 Response Actions

| Action | Time | Outcome |
|--------|------|---------|
| {{ACTION}} | {{ACTION_TIME}} | {{ACTION_OUTCOME}} |

### 3.3 What Worked Well
- {{WORKED_WELL}}

### 3.4 What Could Be Improved
- {{COULD_IMPROVE}}

---

## 4. Technical Details

### 4.1 Error Logs
```
{{ERROR_LOGS}}
```

### 4.2 Affected Code
**File**: `{{FILE_PATH}}`
```{{LANGUAGE}}
{{CODE_SNIPPET}}
```

### 4.3 Configuration at Time of Incident
```yaml
{{INCIDENT_CONFIG}}
```

---

## 5. Resolution

### 5.1 Immediate Fix
{{IMMEDIATE_FIX}}

### 5.2 Long-term Solution
{{LONG_TERM_SOLUTION}}

### 5.3 Verification
```
{{VERIFICATION_OUTPUT}}
```

---

## 6. Action Items

| Priority | Action | Owner | Due Date | Status |
|----------|--------|-------|----------|--------|
| P0 | {{ACTION_ITEM}} | {{OWNER}} | {{DUE_DATE}} | {{STATUS}} |

---

## 7. Lessons Learned

### 7.1 Key Takeaways
1. {{TAKEAWAY_1}}
2. {{TAKEAWAY_2}}

### 7.2 Process Improvements
- {{PROCESS_IMPROVEMENT}}

### 7.3 Documentation Updates Needed
- [ ] {{DOC_UPDATE}}

---

## Appendix

### A. Related Incidents
| ID | Date | Similarity |
|----|------|------------|
| {{RELATED_ID}} | {{RELATED_DATE}} | {{SIMILARITY}} |

### B. References
- {{REFERENCE}}
