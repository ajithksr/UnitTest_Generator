#include "complex_source.hpp"
#include <iostream>
#include <algorithm>
#include <cstdlib>

Processor::Processor() : state_val(0), is_initialized(true) {}

bool Processor::processPacket(const DataPacket& packet) {
    if (!validatePayload(packet.payload)) {
        return false;
    }

    switch (packet.type) {
        case SignalType::START:
            state_val = 1;
            break;
        case SignalType::STOP:
            state_val = 0;
            break;
        case SignalType::PAUSE:
            state_val = 2;
            break;
        case SignalType::RESUME:
            state_val = 1;
            break;
        case SignalType::RESET:
            state_val = 0;
            history.clear();
            break;
        default:
            return false;
    }

    updateInternalState(packet.type);
    recordHistory(packet.id);
    return true;
}

int Processor::performLocalOperation(int val) {
    auto multiplier = [this](int v) {
        return v * (this->state_val + 1);
    };
    return multiplier(val);
}

bool Processor::checkSystemEnvironment(const std::string& var_name) {
    const char* val = std::getenv(var_name.c_str());
    if (val == nullptr) {
        return false;
    }
    return std::string(val) == "ENABLED";
}

void Processor::runComplexCalculation(std::vector<int>& data) {
    if (data.empty()) return;
    
    std::sort(data.begin(), data.end(), [](int a, int b) {
        return a > b;
    });
    
    for (auto& v : data) {
        v = performLocalOperation(v);
    }
}

int Processor::getVersion() {
    return (VERSION_MAJOR << 8) | VERSION_MINOR;
}

void Processor::updateInternalState(SignalType signal) {
    if (signal == SignalType::START) {
        std::cout << "Starting processor..." << std::endl;
    }
}

bool Processor::validatePayload(const std::string& payload) {
    return !payload.empty() && payload.length() < MAX_BUFFER_SIZE;
}

void Processor::recordHistory(int id) {
    history.push_back(id);
}
