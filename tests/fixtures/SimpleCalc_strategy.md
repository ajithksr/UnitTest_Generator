# Test Strategy for `SimpleCalc.c`

**Source File:** `/home/ajith/Documents/git/antigravity/UT_tests/tests/fixtures/SimpleCalc.c`

## Function Coverage Summary

| Function | Kind | Access | Lang | Covered? | Complexity |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `calc_add` | free_function | none | C | ❌ NO | 1 |
| `calc_subtract` | free_function | none | C | ❌ NO | 1 |
| `calc_multiply` | free_function | none | C | ❌ NO | 1 |
| `calc_divide` | free_function | none | C | ❌ NO | 2 |
| `calc_clamp` | free_function | none | C | ❌ NO | 3 |
| `calc_strnlen` | free_function | none | C | ❌ NO | 4 |

## Detailed Strategy per Function

### `calc_add`
- **Signature:** `calc_add(int, int)`
- **Location:** `SimpleCalc.c:9`
- **Kind:** `free_function`
- **Language:** `C`
- **Namespace:** `global`
- **Class:** `None`
- **Static:** `False`
- **Access:** `none`
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

### `calc_subtract`
- **Signature:** `calc_subtract(int, int)`
- **Location:** `SimpleCalc.c:13`
- **Kind:** `free_function`
- **Language:** `C`
- **Namespace:** `global`
- **Class:** `None`
- **Static:** `False`
- **Access:** `none`
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

### `calc_multiply`
- **Signature:** `calc_multiply(int, int)`
- **Location:** `SimpleCalc.c:17`
- **Kind:** `free_function`
- **Language:** `C`
- **Namespace:** `global`
- **Class:** `None`
- **Static:** `False`
- **Access:** `none`
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

### `calc_divide`
- **Signature:** `calc_divide(double, double)`
- **Location:** `SimpleCalc.c:21`
- **Kind:** `free_function`
- **Language:** `C`
- **Namespace:** `global`
- **Class:** `None`
- **Static:** `False`
- **Access:** `none`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - Failure Injection: __errno_location throws/returns error
  - MCDC: Verify 2 logical paths
- **Boundary Cases:**
  - Boundary [a]: std::numeric_limits<double>::max()
  - Boundary [a]: std::numeric_limits<double>::min() (smallest positive)
  - Boundary [a]: 0.0 and -0.0
  - Boundary [a]: NaN, +Inf, -Inf
  - Boundary [b]: std::numeric_limits<double>::max()
  - Boundary [b]: std::numeric_limits<double>::min() (smallest positive)
  - Boundary [b]: 0.0 and -0.0
  - Boundary [b]: NaN, +Inf, -Inf
- **Equivalence Partition Cases:**
  - EP [a]: Typical positive real (valid partition)
  - EP [a]: Typical negative real (valid partition if signed)
  - EP [a]: Very small denormalized value
  - EP [b]: Typical positive real (valid partition)
  - EP [b]: Typical negative real (valid partition if signed)
  - EP [b]: Very small denormalized value
- **Mocks Needed:**
  - Mock for __errno_location
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Cover all 2 logical path combinations.

### `calc_clamp`
- **Signature:** `calc_clamp(int, int, int)`
- **Location:** `SimpleCalc.c:29`
- **Kind:** `free_function`
- **Language:** `C`
- **Namespace:** `global`
- **Class:** `None`
- **Static:** `False`
- **Access:** `none`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
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

### `calc_strnlen`
- **Signature:** `calc_strnlen(const char *, int)`
- **Location:** `SimpleCalc.c:35`
- **Kind:** `free_function`
- **Language:** `C`
- **Namespace:** `global`
- **Class:** `None`
- **Static:** `False`
- **Access:** `none`
- **Suggested Test Cases:**
  - Positive Case
  - Negative Case
  - Boundary Case
  - MCDC: Verify 4 logical paths
- **Boundary Cases:**
  - Boundary [str]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [str]: value = 0 (zero boundary)
  - Boundary [str]: value = -1 and +1 (near-zero)
  - Boundary [max_len]: INT_MIN / INT_MAX (overflow edge)
  - Boundary [max_len]: value = 0 (zero boundary)
  - Boundary [max_len]: value = -1 and +1 (near-zero)
- **Equivalence Partition Cases:**
  - EP [str]: Typical positive value (valid partition)
  - EP [str]: Typical negative value (if signed, valid partition)
  - EP [str]: Zero (border between partitions)
  - EP [str]: Out-of-range / invalid value (invalid partition)
  - EP [max_len]: Typical positive value (valid partition)
  - EP [max_len]: Typical negative value (if signed, valid partition)
  - EP [max_len]: Zero (border between partitions)
  - EP [max_len]: Out-of-range / invalid value (invalid partition)
- **MCDC Requirements:**
  - MCDC: Complexity is 4. Cover all 4 logical path combinations.
