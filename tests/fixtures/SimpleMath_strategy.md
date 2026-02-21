# Test Strategy for `SimpleMath.cpp`

**Source File:** `/home/ajith/Documents/git/antigravity/UT_tests/tests/fixtures/SimpleMath.cpp`

## Function Coverage Summary

| Function | Covered? | Mocks Needed | Complexity |
| :--- | :---: | :--- | :---: |
| `add` | ✅ YES | - | 1 |
| `subtract` | ✅ YES | - | 1 |
| `divide` | ❌ NO | Mock for invalid_argument | 2 |

## Detailed Strategy per Function

### `add`
- **Signature:** `add(int, int)`
- **Location:** `SimpleMath.cpp:6`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Existing Tests:**
  - SimpleMathTest.AddTests
- **Suggested Test Cases:**
  - Additional Verification

### `subtract`
- **Signature:** `subtract(int, int)`
- **Location:** `SimpleMath.cpp:10`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Existing Tests:**
  - SimpleMathStub.SubtractTest
- **Suggested Test Cases:**
  - Additional Verification

### `divide`
- **Signature:** `divide(int, int)`
- **Location:** `SimpleMath.cpp:14`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Failure Injection: invalid_argument throws/returns error
  - MCDC: Verify 2 logical paths
- **Mocks Needed:**
  - Mock for invalid_argument
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Need to cover all path combinations.
