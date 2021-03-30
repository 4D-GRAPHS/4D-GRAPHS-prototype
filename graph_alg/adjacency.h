#pragma once

#include<vector>
#include<string>

#include "frames.h"

struct sAdjacency {
    int from;
    int to;
    double weight;
    int rank;
    int ranked;
};

class cAdjacency {
    std::vector<sAdjacency> adjacency;
public:
    cAdjacency() {};
    bool readFile(std::string f, cFrames *frames);
    std::vector<sAdjacency>* getAdjacency() {return &adjacency;};

    void dump();
};
