#ifndef COMPLEX_SOURCE_HPP
#define COMPLEX_SOURCE_HPP

#include <string>
#include <vector>

#define MAX_BUFFER_SIZE 1024
#define VERSION_MAJOR 1
#define VERSION_MINOR 0

enum class SignalType {
    START,
    STOP,
    PAUSE,
    RESUME,
    RESET
};

struct DataPacket {
    int id;
    std::string payload;
    SignalType type;
};

class Processor {
public:
    Processor();
    bool processPacket(const DataPacket& packet);
    static int getVersion();
    
    // New methods for verification
    int performLocalOperation(int val);
    bool checkSystemEnvironment(const std::string& var_name);
    void runComplexCalculation(std::vector<int>& data);

protected:
    void updateInternalState(SignalType signal);
    int state_val;
    bool is_initialized;

private:
    bool validatePayload(const std::string& payload);
    std::vector<int> history;
    void recordHistory(int id);
};

#endif // COMPLEX_SOURCE_HPP
