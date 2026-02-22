# Test Strategy for `SimpleMath.cpp`

**Source File:** `/home/ajith/Documents/git/antigravity/UT_tests/tests/fixtures/SimpleMath.cpp`

## Function Coverage Summary

| Function | Kind | Access | Lang | Covered? | Complexity |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `add` | public_method | public | C++ | ❌ NO | 1 |
| `subtract` | public_method | public | C++ | ❌ NO | 1 |
| `divide` | public_method | public | C++ | ❌ NO | 2 |
| `clamp` | static_method 🔒static | public | C++ | ❌ NO | 3 |
| `isValidDivisor` | static_method 🔒static | public | C++ | ❌ NO | 1 |
| `scaleResult` | protected_method | protected | C++ | ❌ NO | 2 |
| `checkOverflow` | private_method | private | C++ | ❌ NO | 3 |
| `applySign` | private_method | private | C++ | ❌ NO | 2 |

## Detailed Strategy per Function

### `add`
- **Signature:** `add(int, int)`
- **Location:** `SimpleMath.cpp:9`
- **Kind:** `public_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `public`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
- **Boundary Cases:**
  - Boundary [a]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [a]: value = 0 (zero boundary)
  - Boundary [a]: value = -1 and +1 (near-zero)
  - Boundary [b]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [b]: value = 0 (zero boundary)
  - Boundary [b]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [a]: Typical positive value (valid partition)
  - EP [a]: Typical negative value (if signed, valid partition)
  - EP [a]: Zero (border between partitions)
  - EP [a]: Out-of-range / invalid value (invalid partition)
  - EP [b]: Typical positive value (valid partition)
  - EP [b]: Typical negative value (if signed, valid partition)
  - EP [b]: Zero (border between partitions)
  - EP [b]: Out-of-range / invalid value (invalid partition)

### `subtract`
- **Signature:** `subtract(int, int)`
- **Location:** `SimpleMath.cpp:13`
- **Kind:** `public_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `public`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
- **Boundary Cases:**
  - Boundary [a]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [a]: value = 0 (zero boundary)
  - Boundary [a]: value = -1 and +1 (near-zero)
  - Boundary [b]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [b]: value = 0 (zero boundary)
  - Boundary [b]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [a]: Typical positive value (valid partition)
  - EP [a]: Typical negative value (if signed, valid partition)
  - EP [a]: Zero (border between partitions)
  - EP [a]: Out-of-range / invalid value (invalid partition)
  - EP [b]: Typical positive value (valid partition)
  - EP [b]: Typical negative value (if signed, valid partition)
  - EP [b]: Zero (border between partitions)
  - EP [b]: Out-of-range / invalid value (invalid partition)

### `divide`
- **Signature:** `divide(int, int)`
- **Location:** `SimpleMath.cpp:17`
- **Kind:** `public_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `public`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Failure Injection: invalid_argument throws/returns error
  - MCDC: Verify 2 logical paths
- **Boundary Cases:**
  - Boundary [a]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [a]: value = 0 (zero boundary)
  - Boundary [a]: value = -1 and +1 (near-zero)
  - Boundary [b]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [b]: value = 0 (zero boundary)
  - Boundary [b]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [a]: Typical positive value (valid partition)
  - EP [a]: Typical negative value (if signed, valid partition)
  - EP [a]: Zero (border between partitions)
  - EP [a]: Out-of-range / invalid value (invalid partition)
  - EP [b]: Typical positive value (valid partition)
  - EP [b]: Typical negative value (if signed, valid partition)
  - EP [b]: Zero (border between partitions)
  - EP [b]: Out-of-range / invalid value (invalid partition)
- **Mocks Needed:**
  - Mock for invalid_argument
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Cover all 2 logical path combinations.

### `clamp`
- **Signature:** `clamp(int, int, int)`
- **Location:** `SimpleMath.cpp:26`
- **Kind:** `static_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `True`
- **Access:** `public`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Static: call directly without class instance — verify thread-safety if applicable
  - MCDC: Verify 3 logical paths
- **Boundary Cases:**
  - Boundary [value]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [value]: value = 0 (zero boundary)
  - Boundary [value]: value = -1 and +1 (near-zero)
  - Boundary [min_val]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [min_val]: value = 0 (zero boundary)
  - Boundary [min_val]: value = -1 and +1 (near-zero)
  - Boundary [max_val]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [max_val]: value = 0 (zero boundary)
  - Boundary [max_val]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [value]: Typical positive value (valid partition)
  - EP [value]: Typical negative value (if signed, valid partition)
  - EP [value]: Zero (border between partitions)
  - EP [value]: Out-of-range / invalid value (invalid partition)
  - EP [min_val]: Typical positive value (valid partition)
  - EP [min_val]: Typical negative value (if signed, valid partition)
  - EP [min_val]: Zero (border between partitions)
  - EP [min_val]: Out-of-range / invalid value (invalid partition)
  - EP [max_val]: Typical positive value (valid partition)
  - EP [max_val]: Typical negative value (if signed, valid partition)
  - EP [max_val]: Zero (border between partitions)
  - EP [max_val]: Out-of-range / invalid value (invalid partition)
- **MCDC Requirements:**
  - MCDC: Complexity is 3. Cover all 3 logical path combinations.

### `isValidDivisor`
- **Signature:** `isValidDivisor(int)`
- **Location:** `SimpleMath.cpp:32`
- **Kind:** `static_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `True`
- **Access:** `public`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Static: call directly without class instance — verify thread-safety if applicable
- **Boundary Cases:**
  - Boundary [divisor]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [divisor]: value = 0 (zero boundary)
  - Boundary [divisor]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [divisor]: Typical positive value (valid partition)
  - EP [divisor]: Typical negative value (if signed, valid partition)
  - EP [divisor]: Zero (border between partitions)
  - EP [divisor]: Out-of-range / invalid value (invalid partition)

### `scaleResult`
- **Signature:** `scaleResult(int, int)`
- **Location:** `SimpleMath.cpp:38`
- **Kind:** `protected_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `protected`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Access: protected method — test via public API, friend class, or expose via test subclass
  - MCDC: Verify 2 logical paths
- **Boundary Cases:**
  - Boundary [value]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [value]: value = 0 (zero boundary)
  - Boundary [value]: value = -1 and +1 (near-zero)
  - Boundary [factor]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [factor]: value = 0 (zero boundary)
  - Boundary [factor]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [value]: Typical positive value (valid partition)
  - EP [value]: Typical negative value (if signed, valid partition)
  - EP [value]: Zero (border between partitions)
  - EP [value]: Out-of-range / invalid value (invalid partition)
  - EP [factor]: Typical positive value (valid partition)
  - EP [factor]: Typical negative value (if signed, valid partition)
  - EP [factor]: Zero (border between partitions)
  - EP [factor]: Out-of-range / invalid value (invalid partition)
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Cover all 2 logical path combinations.

### `checkOverflow`
- **Signature:** `checkOverflow(int, int)`
- **Location:** `SimpleMath.cpp:45`
- **Kind:** `private_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `private`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Access: private method — test via public API, friend class, or expose via test subclass
  - MCDC: Verify 3 logical paths
- **Boundary Cases:**
  - Boundary [a]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [a]: value = 0 (zero boundary)
  - Boundary [a]: value = -1 and +1 (near-zero)
  - Boundary [b]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [b]: value = 0 (zero boundary)
  - Boundary [b]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [a]: Typical positive value (valid partition)
  - EP [a]: Typical negative value (if signed, valid partition)
  - EP [a]: Zero (border between partitions)
  - EP [a]: Out-of-range / invalid value (invalid partition)
  - EP [b]: Typical positive value (valid partition)
  - EP [b]: Typical negative value (if signed, valid partition)
  - EP [b]: Zero (border between partitions)
  - EP [b]: Out-of-range / invalid value (invalid partition)
- **MCDC Requirements:**
  - MCDC: Complexity is 3. Cover all 3 logical path combinations.

### `applySign`
- **Signature:** `applySign(int, bool)`
- **Location:** `SimpleMath.cpp:51`
- **Kind:** `private_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `private`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Access: private method — test via public API, friend class, or expose via test subclass
  - MCDC: Verify 2 logical paths
- **Boundary Cases:**
  - Boundary [magnitude]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [magnitude]: value = 0 (zero boundary)
  - Boundary [magnitude]: value = -1 and +1 (near-zero)
  - Boundary [negative]: true
  - Boundary [negative]: false
- **Equivalence Partition Cases:**
  - EP [magnitude]: Typical positive value (valid partition)
  - EP [magnitude]: Typical negative value (if signed, valid partition)
  - EP [magnitude]: Zero (border between partitions)
  - EP [magnitude]: Out-of-range / invalid value (invalid partition)
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Cover all 2 logical path combinations.
