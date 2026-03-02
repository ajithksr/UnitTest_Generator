// Auto-generated unit test file
// Source: SimpleCalc.h  |  Language: C
#include <gtest/gtest.h>
#include <gmock/gmock.h>

// C source — include via extern "C" linkage
extern "C" {

#include "SimpleCalc.h"

}




// ───────────────────────────────────────────────────────────────────────────
// Function : calc_add
// Signature: calc_add(int, int)
// Kind     : free_function
// Access   : none
// Language : C
// ───────────────────────────────────────────────────────────────────────────









TEST(GlobalFunctions, calc_add_Coverage) {
    
TEST(CalcAddTest, TypicalPositiveValues) {
    // Test with typical positive values
    EXPECT_EQ(calc_add(1, 2), 3);
    EXPECT_EQ(calc_add(5, 7), 12);
    EXPECT_EQ(calc_add(100, 200), 300);
}

TEST(CalcAddTest, TypicalNegativeValues) {
    // Test with typical negative values
    EXPECT_EQ(calc_add(-1, -2), -3);
    EXPECT_EQ(calc_add(-5, -7), -12);
    EXPECT_EQ(calc_add(-100, -200), -300);
}

TEST(CalcAddTest, ZeroAsParameter) {
    // Test with zero as a parameter
    EXPECT_EQ(calc_add(0, 5), 5);
    EXPECT_EQ(calc_add(5, 0), 5);
    EXPECT_EQ(calc_add(0, 0), 0);
}

TEST(CalcAddTest, BoundaryCases) {
    // Test INT_MIN and INT_MAX as parameters (boundary cases)
    EXPECT_EQ(calc_add(INT_MIN, 1), INT_MIN + 1);
    EXPECT_EQ(calc_add(1, INT_MIN), INT_MIN + 1);
    EXPECT_EQ(calc_add(INT_MIN, INT_MAX), INT_MAX - 1);
    EXPECT_EQ(calc_add(INT_MAX, INT_MIN), INT_MAX - 1);
}

TEST(CalcAddTest, NearZeroValues) {
    // Test near-zero values (-1 and +1)
    EXPECT_EQ(calc_add(-1, 1), 0);
    EXPECT_EQ(calc_add(1, -1), 0);
}
    
}





// ───────────────────────────────────────────────────────────────────────────
// Function : calc_subtract
// Signature: calc_subtract(int, int)
// Kind     : free_function
// Access   : none
// Language : C
// ───────────────────────────────────────────────────────────────────────────









TEST(GlobalFunctions, calc_subtract_Coverage) {
    
TEST(CalcSubtractTest, TestCalcSubtractWithIntMinAndMax) {
    // Test INT_MIN and INT_MAX
    EXPECT_EQ(calc_subtract(INT_MIN, INT_MAX), INT_MIN);
    EXPECT_EQ(calc_subtract(INT_MAX, INT_MIN), -INT_MIN - 1);
}

TEST(CalcSubtractTest, TestCalcSubtractWithZeroValues) {
    // Test a=0, b=0
    EXPECT_EQ(calc_subtract(0, 0), 0);

    // Test a=0, b=-1
    EXPECT_EQ(calc_subtract(0, -1), -1);

    // Test a=0, b=1
    EXPECT_EQ(calc_subtract(0, 1), 1);
}

TEST(CalcSubtractTest, TestCalcSubtractWithNearZeroValues) {
    // Test a=-1, b=1
    EXPECT_EQ(calc_subtract(-1, 1), -2);

    // Test a=-2, b=2
    EXPECT_EQ(calc_subtract(-2, 2), -4);
}

TEST(CalcSubtractTest, TestCalcSubtractWithTypicalPositiveValues) {
    // Test typical positive values
    EXPECT_EQ(calc_subtract(5, 3), 2);
    EXPECT_EQ(calc_subtract(10, 7), 3);
    EXPECT_EQ(calc_subtract(100, 90), 10);
}

TEST(CalcSubtractTest, TestCalcSubtractWithTypicalNegativeValues) {
    // Test typical negative values
    EXPECT_EQ(calc_subtract(-5, -3), -2);
    EXPECT_EQ(calc_subtract(-10, -7), -3);
    EXPECT_EQ(calc_subtract(-100, -90), 10);
}
    
}





// ───────────────────────────────────────────────────────────────────────────
// Function : calc_multiply
// Signature: calc_multiply(int, int)
// Kind     : free_function
// Access   : none
// Language : C
// ───────────────────────────────────────────────────────────────────────────









TEST(GlobalFunctions, calc_multiply_Coverage) {
    
TEST(CalcMultiplyTest, TestCalcMultiplyWithIntMinFirst) {
    EXPECT_EQ(calc_multiply(INT_MIN, 1), INT_MIN);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithIntMaxFirst) {
    EXPECT_EQ(calc_multiply(INT_MAX, 1), INT_MAX);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithIntMinSecond) {
    EXPECT_EQ(calc_multiply(1, INT_MIN), INT_MIN);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithIntMaxSecond) {
    EXPECT_EQ(calc_multiply(1, INT_MAX), INT_MAX);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithZeroBothArguments) {
    EXPECT_EQ(calc_multiply(0, 0), 0);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithNegativeAndPositive) {
    EXPECT_EQ(calc_multiply(-1, 1), -1);
    EXPECT_EQ(calc_multiply(1, -1), -1);
    EXPECT_EQ(calc_multiply(-1, -1), 1);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithTypicalPositiveValue) {
    EXPECT_EQ(calc_multiply(100, 200), 20000);
}

TEST(CalcMultiplyTest, TestCalcMultiplyWithTypicalNegativeValue) {
    EXPECT_EQ(calc_multiply(-100, -200), 20000);
}
    
}





// ───────────────────────────────────────────────────────────────────────────
// Function : calc_divide
// Signature: calc_divide(double, double)
// Kind     : free_function
// Access   : none
// Language : C
// ───────────────────────────────────────────────────────────────────────────









TEST(GlobalFunctions, calc_divide_Coverage) {
    
// Error: Ollama connection failed: HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=120)
    
}





// ───────────────────────────────────────────────────────────────────────────
// Function : calc_clamp
// Signature: calc_clamp(int, int, int)
// Kind     : free_function
// Access   : none
// Language : C
// ───────────────────────────────────────────────────────────────────────────









TEST(GlobalFunctions, calc_clamp_Coverage) {
    
TEST(calc_clamp, ErrorScenario) {
    // Arrange: Set up any necessary inputs and expected outputs
    int lower = 10;
    int upper = 20;
    int value = 30;

    // Act: Call the function under test
    int result = calc_clamp(value, lower, upper);

    // Assert: Verify that the function returns the expected result or throws an exception
    EXPECT_EQ(result, 20); // Assuming the clamp function should return the upper bound when value exceeds it
}
    
}





// ───────────────────────────────────────────────────────────────────────────
// Function : calc_strnlen
// Signature: calc_strnlen(const char *, int)
// Kind     : free_function
// Access   : none
// Language : C
// ───────────────────────────────────────────────────────────────────────────









TEST(GlobalFunctions, calc_strnlen_Coverage) {
    
#include <gtest/gtest.h>
#include <cstring>

// Function under test
size_t calc_strnlen(const char *str, int maxlen) {
    if (str == nullptr) return 0;
    size_t len = 0;
    while (*str && len < maxlen) {
        str++;
        len++;
    }
    return len;
}

TEST(calc_strnlenTest, ErrorOllamaConnectionFailed) {
    // Test case: Ollama connection failed: HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=120)
    // This test case is not directly related to the calc_strnlen function but is mentioned in the comments.
    // It seems like an error message from a hypothetical Ollama connection attempt, which is unrelated to the string length calculation.

    // Expected behavior: The function should handle null pointers gracefully and return 0.
    const char *nullStr = nullptr;
    EXPECT_EQ(calc_strnlen(nullStr, 10), 0);

    // Expected behavior: The function should correctly calculate the length of a non-null string up to maxlen characters.
    const char *testStr = "Hello, World!";
    EXPECT_EQ(calc_strnlen(testStr, 5), 5);
    EXPECT_EQ(calc_strnlen(testStr, 12), 13); // Including null terminator
}
    
}



