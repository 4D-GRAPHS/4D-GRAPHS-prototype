#pragma once

#include <vector>
#include <string>
#include <map>

#include "sequence.h"

class cFrames {
    std::vector<std::string> frames;
    std::map<std::string, int> framesMap;
    int trueFrames;
    int dummyFrames;
    void addProlines(cSequence* const sequence);
public:
    cFrames() : trueFrames(0), dummyFrames(0) {};
    bool readFile(std::string f, cSequence* const sequence);
    std::vector<std::string>* getFrames() {return &frames;};
    int getFrameIndex(const std::string &frame);
    int getTrueFramesNum() {return trueFrames;};
    int getDummyFramesNum() {return dummyFrames;};
    void addDummyFrames(int num);

    void dump();
};
