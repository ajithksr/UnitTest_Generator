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
- **Unified Test Scenarios:**
  - Test add(0, 0) to ensure it returns 0
  - Test add(INT_MIN, INT_MAX) for overflow edge case
  - Test add(-1, +1) and similar near-zero values
  - Verify add(INT_MAX, -1) for overflow edge case
  - Test add(1, -1) and similar near-zero values

### `subtract`
- **Signature:** `subtract(int, int)`
- **Location:** `SimpleMath.cpp:13`
- **Kind:** `public_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `public`
- **Unified Test Scenarios:**
  - Test subtract(INT_MIN, INT_MAX) for overflow
  - Test subtract(INT_MAX, INT_MIN) for overflow
  - Test subtract(0, 0) returns 0
  - Test subtract(-1, -1) returns 0
  - Test subtract(1, 1) returns 0
  - Test subtract(INT_MIN, 0) for underflow
  - Test subtract(INT_MAX, 0) for overflow
  - Test subtract(0, INT_MIN) for underflow
  - Test subtract(0, INT_MAX) for overflow

### `divide`
- **Signature:** `divide(int, int)`
- **Location:** `SimpleMath.cpp:17`
- **Kind:** `public_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `public`
- **Unified Test Scenarios:**
  - Test division by zero
  - Test division with INT_MIN as numerator
  - Test division with INT_MAX as numerator
  - Test division with INT_MIN as denominator
  - Test division with INT_MAX as denominator
  - Test division with 0 as numerator
  - Test division with 0 as denominator
  - Test division with -1 as numerator and -1 as denominator
  - Test division with -1 as numerator and +1 as denominator
  - Test division with +1 as numerator and -1 as denominator
  - Test division with +1 as numerator and +1 as denominator
- **Mocks Needed:**
  - Mock for invalid_argument
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Ensure all 2 logical decision branches are covered.

### `clamp`
- **Signature:** `clamp(int, int, int)`
- **Location:** `SimpleMath.cpp:26`
- **Kind:** `static_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `True`
- **Access:** `public`
- **Unified Test Scenarios:**
  - // Error: Ollama connection failed: HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=120)
  - NOTE: Call directly via class scope (Static method)
- **MCDC Requirements:**
  - MCDC: Complexity is 3. Ensure all 3 logical decision branches are covered.

### `isValidDivisor`
- **Signature:** `isValidDivisor(int)`
- **Location:** `SimpleMath.cpp:32`
- **Kind:** `static_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `True`
- **Access:** `public`
- **Unified Test Scenarios:**
  - Test isValidDivisor with INT_MIN
  - Test isValidDivisor with INT_MAX
  - Test isValidDivisor with zero (0)
  - Test isValidDivisor with -1
  - Test isValidDivisor with 1
  - NOTE: Call directly via class scope (Static method)

### `scaleResult`
- **Signature:** `scaleResult(int, int)`
- **Location:** `SimpleMath.cpp:38`
- **Kind:** `protected_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `protected`
- **Unified Test Scenarios:**
  - Test scaleResult with typical positive value (e.g., 10, 100)
  - Test scaleResult with typical negative value (e.g., -10, -100)
  - Test scaleResult with zero (value = 0)
  - Test scaleResult with near-zero values (value = -1, +1)
  - Test scaleResult with INT_MIN and INT_MAX as value
  - Test scaleResult with typical positive factor (e.g., 2, 5)
  - Test scaleResult with typical negative factor (e.g., -2, -5)
  - Test scaleResult with zero factor (factor = 0)
  - Test scaleResult with near-zero factors (factor = -1, +1)
  - Test scaleResult with INT_MIN and INT_MAX as factor
  - Test scaleResult with overflow edge cases for value and factor
  - NOTE: Test via public API or test subclass (Access: protected)
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Ensure all 2 logical decision branches are covered.

### `checkOverflow`
- **Signature:** `checkOverflow(int, int)`
- **Location:** `SimpleMath.cpp:45`
- **Kind:** `private_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `private`
- **Unified Test Scenarios:**
  - Test checkOverflow with INT_MIN and positive boundary
  - Test checkOverflow with INT_MAX and negative boundary
  - Test checkOverflow with zero values for both a and b
  - Test checkOverflow with near-zero values for both a and b
  - Test checkOverflow with typical positive value for a and typical positive value for b
  - Test checkOverflow with typical negative value for a and typical negative value for b
  - Test checkOverflow with zero value for a and typical positive value for b
  - Test checkOverflow with zero value for b and typical positive value for a
  - NOTE: Test via public API or test subclass (Access: private)
- **MCDC Requirements:**
  - MCDC: Complexity is 3. Ensure all 3 logical decision branches are covered.

### `applySign`
- **Signature:** `applySign(int, bool)`
- **Location:** `SimpleMath.cpp:51`
- **Kind:** `private_method`
- **Language:** `C++`
- **Namespace:** `MathLib`
- **Class:** `SimpleMath`
- **Static:** `False`
- **Access:** `private`
- **Unified Test Scenarios:**
  - Test applySign with magnitude as INT_MIN and negative as true
  - Test applySign with magnitude as INT_MAX and negative as false
  - Test applySign with magnitude as 0 and negative as true
  - Test applySign with magnitude as 0 and negative as false
  - Test applySign with magnitude as -1 and negative as true
  - Test applySign with magnitude as -1 and negative as false
  - Test applySign with magnitude as 1 and negative as true
  - Test applySign with magnitude as 1 and negative as false
  - NOTE: Test via public API or test subclass (Access: private)
- **MCDC Requirements:**
  - MCDC: Complexity is 2. Ensure all 2 logical decision branches are covered.
