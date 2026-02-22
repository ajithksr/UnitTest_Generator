/**
 * SimpleCalc.c - Plain C implementation for unit testing the C pipeline.
 */
#include "SimpleCalc.h"
#include <errno.h>
#include <string.h>
#include <limits.h>

int calc_add(int a, int b) {
    return a + b;
}

int calc_subtract(int a, int b) {
    return a - b;
}

int calc_multiply(int a, int b) {
    return a * b;
}

double calc_divide(double a, double b) {
    if (b == 0.0) {
        errno = EDOM;
        return 0.0;
    }
    return a / b;
}

int calc_clamp(int value, int min_val, int max_val) {
    if (value < min_val) return min_val;
    if (value > max_val) return max_val;
    return value;
}

int calc_strnlen(const char *str, int max_len) {
    if (str == NULL) return -1;
    int len = 0;
    while (len < max_len && str[len] != '\0') {
        len++;
    }
    if (len == max_len && str[len] != '\0') return -1;
    return len;
}
