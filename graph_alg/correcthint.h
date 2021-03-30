#pragma once

#include <vector>
#include <string>
#include <map>

class cCorrectHint {
    std::vector<std::string> frames;
public:
    cCorrectHint() {};
    bool readFile(std::string f);
    std::vector<std::string>* getFrames() {return &frames;};

    void dump();
};
