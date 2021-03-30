#pragma once

#include<vector>

#include "frames.h"

class cFramesScore {
    std::vector<double> score;
public:
    cFramesScore() {};
    bool readFile(std::string f, cFrames *frames);
    double getScore(int frame) {return score[frame];};

    void dump();
};
