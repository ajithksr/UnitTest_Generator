#include <gtest/gtest.h>
#include "SimpleMath.hpp"

namespace MathLib {

class SimpleMathTest : public ::testing::Test {
protected:
    SimpleMath math;
};

TEST_F(SimpleMathTest, AddTests) {
    EXPECT_EQ(math.add(1, 2), 3);
}

TEST(SimpleMathStub, SubtractTest) {
    SimpleMath m;
    EXPECT_EQ(m.subtract(5, 3), 2);
}

}
