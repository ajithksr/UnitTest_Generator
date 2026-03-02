#include <gtest/gtest.h>
#include "complex_source.hpp"

TEST(Processor_Global, VersionCheck) {
    EXPECT_EQ(Processor::getVersion(), 0x0100);
}

TEST(ProcessorTest, BasicProcess) {
    Processor proc;
    DataPacket packet;
    packet.id = 1;
    packet.payload = "HelloWorld";
    packet.type = SignalType::START;
    EXPECT_TRUE(proc.processPacket(packet));
}

TEST(ProcessorTest, SystemEnvCheck) {
    Processor proc;
    EXPECT_FALSE(proc.checkSystemEnvironment("NON_EXISTENT"));
}
