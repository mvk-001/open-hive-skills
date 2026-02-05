# Debug Investigation: {{TITLE}}

**Report ID**: DBG-{{DATE}}-{{SEQ}}
**Author**: {{AUTHOR}}
**Date**: {{DATE}}
**Status**: {{STATUS}}

---

## Executive Summary

{{EXECUTIVE_SUMMARY}}

**Symptom**: {{SYMPTOM}}
**Root Cause**: {{ROOT_CAUSE}}
**Resolution**: {{RESOLUTION}}

---

## 1. Problem Statement

### 1.1 Observed Behavior
{{OBSERVED_BEHAVIOR}}

### 1.2 Expected Behavior
{{EXPECTED_BEHAVIOR}}

### 1.3 Reproduction Steps
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

### 1.4 Environment
| Property | Value |
|----------|-------|
| OS | {{OS}} |
| Runtime | {{RUNTIME}} |
| Version | {{VERSION}} |
| Config | {{CONFIG}} |

---

## 2. Investigation

### 2.1 Hypothesis Log

| # | Hypothesis | Test | Result | Verdict |
|---|------------|------|--------|---------|
| 1 | {{HYPOTHESIS_1}} | {{TEST_1}} | {{RESULT_1}} | ✅/❌ |
| 2 | {{HYPOTHESIS_2}} | {{TEST_2}} | {{RESULT_2}} | ✅/❌ |

### 2.2 Diagnostic Commands

```bash
{{DIAGNOSTIC_COMMAND}}
```

**Output:**
```
{{DIAGNOSTIC_OUTPUT}}
```

### 2.3 Code Analysis

**Suspicious File**: `{{FILE_PATH}}`
**Line(s)**: {{LINE_NUMBERS}}

```{{LANGUAGE}}
{{CODE_SNIPPET}}
```

**Issue**: {{CODE_ISSUE}}

### 2.4 Log Analysis

```
{{RELEVANT_LOGS}}
```

**Key Observation**: {{LOG_OBSERVATION}}

---

## 3. Root Cause

### 3.1 The Bug
{{BUG_DESCRIPTION}}

### 3.2 Why It Occurred
{{WHY_OCCURRED}}

### 3.3 Impact Assessment
| Scope | Impact |
|-------|--------|
| {{SCOPE}} | {{IMPACT}} |

---

## 4. Solution

### 4.1 Fix Applied

**File**: `{{FIX_FILE}}`

```diff
{{FIX_DIFF}}
```

### 4.2 Why This Fix Works
{{FIX_EXPLANATION}}

### 4.3 Alternative Solutions Considered
| Solution | Pros | Cons | Rejected Because |
|----------|------|------|------------------|
| {{ALT_SOLUTION}} | {{PROS}} | {{CONS}} | {{REJECTION_REASON}} |

---

## 5. Verification

### 5.1 Test Command
```bash
{{TEST_COMMAND}}
```

### 5.2 Before Fix
```
{{BEFORE_OUTPUT}}
```

### 5.3 After Fix
```
{{AFTER_OUTPUT}}
```

### 5.4 Regression Check
- [ ] Related functionality still works
- [ ] No new errors in logs
- [ ] Performance unchanged

---

## 6. Prevention

### 6.1 How to Prevent Recurrence
1. {{PREVENTION_1}}
2. {{PREVENTION_2}}

### 6.2 Tests to Add
```{{LANGUAGE}}
{{TEST_CODE}}
```

### 6.3 Documentation Updates
- [ ] {{DOC_UPDATE}}

---

## 7. Lessons Learned

- {{LESSON}}

---

## Appendix

### A. Full Stack Trace
```
{{STACK_TRACE}}
```

### B. Related Issues
- {{RELATED_ISSUE}}

### C. References
- {{REFERENCE}}
