#pragma once
#include <string>
#include <stdexcept>

namespace MathLib {

class SimpleMath {
public:
    // Public methods
    int add(int a, int b);
    int subtract(int a, int b);
    double divide(int a, int b);

    // Static utility — no instance needed
    static int clamp(int value, int min_val, int max_val);
    static bool isValidDivisor(int divisor);

protected:
    // Protected helper — only accessible to subclasses
    int scaleResult(int value, int factor);

private:
    // Private helper — internal implementation detail
    bool checkOverflow(int a, int b) const;
    int applySign(int magnitude, bool negative) const;
};

}  // namespace MathLib
