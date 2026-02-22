#include "SimpleMath.hpp"
#include <stdexcept>
#include <climits>

namespace MathLib {

// ─── Public Methods ─────────────────────────────────────────────────────────

int SimpleMath::add(int a, int b) {
    return a + b;
}

int SimpleMath::subtract(int a, int b) {
    return a - b;
}

double SimpleMath::divide(int a, int b) {
    if (b == 0) {
        throw std::invalid_argument("Division by zero");
    }
    return static_cast<double>(a) / b;
}

// ─── Static Methods ──────────────────────────────────────────────────────────

/*static*/ int SimpleMath::clamp(int value, int min_val, int max_val) {
    if (value < min_val) return min_val;
    if (value > max_val) return max_val;
    return value;
}

/*static*/ bool SimpleMath::isValidDivisor(int divisor) {
    return divisor != 0;
}

// ─── Protected Methods ───────────────────────────────────────────────────────

int SimpleMath::scaleResult(int value, int factor) {
    if (factor == 0) return 0;
    return value * factor;
}

// ─── Private Methods ─────────────────────────────────────────────────────────

bool SimpleMath::checkOverflow(int a, int b) const {
    if (b > 0 && a > INT_MAX - b) return true;
    if (b < 0 && a < INT_MIN - b) return true;
    return false;
}

int SimpleMath::applySign(int magnitude, bool negative) const {
    return negative ? -magnitude : magnitude;
}

}  // namespace MathLib
