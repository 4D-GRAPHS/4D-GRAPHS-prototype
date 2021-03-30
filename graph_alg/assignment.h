#pragma once

#include<vector>
#include<string>

#include "frames.h"
#include "sequence.h"

struct sAssignment {
    double weight;
    int rank;
    int ranked;
};

class cAssignment {
    std::vector<std::vector<sAssignment>> assignment;
public:
    cAssignment() {};
    bool readFile(std::string f, cFrames *frames, cSequence *sequence);
    double getScore(int frame, int acid) {return assignment[frame][acid].weight;};
    int getRank(int frame, int acid) {return assignment[frame][acid].rank;};
    int getRanked(int frame, int acid) {return assignment[frame][acid].ranked;};

    void dump();
};
