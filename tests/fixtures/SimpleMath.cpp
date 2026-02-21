#include "SimpleMath.hpp"
#include <stdexcept>

namespace MathLib {

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

}
