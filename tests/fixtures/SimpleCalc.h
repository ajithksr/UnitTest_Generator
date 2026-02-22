/**
 * SimpleCalc.h - Plain C header for unit testing the C pipeline.
 */
#ifndef SIMPLE_CALC_H
#define SIMPLE_CALC_H

#include <stdint.h>

/** Add two integers. */
int calc_add(int a, int b);

/** Subtract b from a. */
int calc_subtract(int a, int b);

/** Multiply two integers — may overflow for extreme inputs. */
int calc_multiply(int a, int b);

/**
 * Divide a by b.
 * Returns 0 and sets errno to EDOM when b == 0.
 */
double calc_divide(double a, double b);

/**
 * Clamp value into [min_val, max_val].
 * Returns min_val when value < min_val, max_val when value > max_val.
 */
int calc_clamp(int value, int min_val, int max_val);

/**
 * Safe string length using a maximum buffer size.
 * Returns -1 if str is NULL or length exceeds max_len.
 */
int calc_strnlen(const char *str, int max_len);

#endif /* SIMPLE_CALC_H */
