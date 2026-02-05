# Debug Investigation: OpenAPI Generator Boolean Serialization Bug

**Report ID**: DBG-20260204-2140
**Author**: Archie (Codex Sub-agent)
**Date**: 2026-02-04
**Status**: Resolved

---

## Executive Summary

During testing of the newly created OpenAPI-to-Skill generator, the generated `api_client.py` failed with a `NameError` for undefined `true`. Root cause: Python boolean `True/False` was being serialized as JavaScript-style `true/false` in generated code. Resolution: Changed string formatting from `.lower()` to direct Python boolean insertion.

**Symptom**: `NameError: name 'true' is not defined`
**Root Cause**: Incorrect boolean serialization in code generation
**Resolution**: Single-line fix in `openapi_to_skill.py`

---

## 1. Problem Statement

### 1.1 Observed Behavior
Generated API client script crashed on import with:
```
NameError: name 'true' is not defined. Did you mean: 'True'?
```

### 1.2 Expected Behavior
Generated script should run without syntax errors and list all available API operations.

### 1.3 Reproduction Steps
1. Run `python openapi_to_skill.py https://petstore3.swagger.io/api/v3/openapi.json --output /tmp/test/`
2. Execute generated client: `python /tmp/test/.../scripts/api_client.py --list`
3. Observe crash

### 1.4 Environment
| Property | Value |
|----------|-------|
| OS | Linux 6.17.0-12-generic |
| Runtime | Python 3.12 |
| Version | openapi_to_skill.py v1.0 |
| Config | Default |

---

## 2. Investigation

### 2.1 Hypothesis Log

| # | Hypothesis | Test | Result | Verdict |
|---|------------|------|--------|---------|
| 1 | Import issue | Check imports | All imports valid | ❌ |
| 2 | Boolean serialization | Inspect generated code | Found `true` instead of `True` | ✅ |

### 2.2 Diagnostic Commands

```bash
python3 /tmp/test-skills/swagger-petstore-openapi-3-0/scripts/api_client.py --list
```

**Output:**
```
Traceback (most recent call last):
  File ".../api_client.py", line 93, in <module>
    "has_body": true,
                ^^^^
NameError: name 'true' is not defined. Did you mean: 'True'?
```

### 2.3 Code Analysis

**Suspicious File**: `skills/openapi-integrator/scripts/openapi_to_skill.py`
**Line(s)**: ~350

```python
        "has_body": {str(op['request_body'] is not None).lower()},
```

**Issue**: `str(True).lower()` produces `'true'` (JavaScript boolean), but Python requires `True`.

### 2.4 Log Analysis

```
File ".../api_client.py", line 93
    "has_body": true,
                ^^^^
NameError: name 'true' is not defined
```

**Key Observation**: The generated code contained JavaScript-style boolean literals.

---

## 3. Root Cause

### 3.1 The Bug
The code generation template used `str(bool_value).lower()` to serialize booleans, which converts Python's `True/False` to lowercase `true/false` strings. When this is inserted into generated Python code, it creates invalid syntax.

### 3.2 Why It Occurred
Developer oversight—the `.lower()` call was added thinking about JSON output (where booleans are lowercase), but the generated code is Python, not JSON.

### 3.3 Impact Assessment
| Scope | Impact |
|-------|--------|
| All generated skills | 100% of generated clients would fail |
| User experience | Skill unusable without manual fix |

---

## 4. Solution

### 4.1 Fix Applied

**File**: `skills/openapi-integrator/scripts/openapi_to_skill.py`

```diff
-        "has_body": {str(op['request_body'] is not None).lower()},
+        "has_body": {op['request_body'] is not None},
```

### 4.2 Why This Fix Works
Direct boolean insertion produces valid Python: `"has_body": True,` or `"has_body": False,`. Python's f-string formatting automatically converts the boolean to its correct representation.

### 4.3 Alternative Solutions Considered
| Solution | Pros | Cons | Rejected Because |
|----------|------|------|------------------|
| Use json.dumps() | Proper serialization | Adds quotes around value | Would need eval() on load |
| Manual True/False strings | Explicit | Error-prone | Same issue could recur |
| Direct insertion | Simple, correct | None | ✅ Chosen |

---

## 5. Verification

### 5.1 Test Command
```bash
python3 skills/openapi-integrator/scripts/openapi_to_skill.py \
  https://petstore3.swagger.io/api/v3/openapi.json \
  --output /tmp/test-skills2/
python3 /tmp/test-skills2/swagger-petstore-openapi-3-0/scripts/api_client.py --list
```

### 5.2 Before Fix
```
NameError: name 'true' is not defined. Did you mean: 'True'?
```

### 5.3 After Fix
```
Available operations:

  addpet
    POST /pet
    Add a new pet to the store.

  updatepet
    PUT /pet
    Update an existing pet.
  ...
```

### 5.4 Regression Check
- [x] Related functionality still works
- [x] No new errors in logs
- [x] Performance unchanged

---

## 6. Prevention

### 6.1 How to Prevent Recurrence
1. Always test generated code by executing it
2. Add unit tests for code generation paths
3. Use AST generation instead of string templates for complex code

### 6.2 Tests to Add
```python
def test_boolean_serialization():
    """Ensure booleans in generated code are valid Python."""
    spec = load_sample_spec()
    client_code = generate_api_client(spec, ...)
    exec(client_code)  # Should not raise
```

### 6.3 Documentation Updates
- [ ] Add "Testing Generated Skills" section to openapi-integrator SKILL.md

---

## 7. Lessons Learned

- Generated code must be tested by execution, not just inspection
- String-based code generation is fragile; consider AST builders for complex cases
- The difference between JSON and Python boolean syntax is subtle but critical

---

## Appendix

### A. Full Stack Trace
```
Traceback (most recent call last):
  File "/tmp/test-skills/swagger-petstore-openapi-3-0/scripts/api_client.py", line 93, in <module>
    "has_body": true,
                ^^^^
NameError: name 'true' is not defined. Did you mean: 'True'?
```

### B. Related Issues
- None (first occurrence)

### C. References
- Python boolean documentation: https://docs.python.org/3/library/stdtypes.html#boolean-type-bool
