#pragma once

#include<vector>
#include<string>

#include "frames.h"
#include "sequence.h"

class cAdjacency3d {
    std::vector<double> adjacency3d;
    int frNum, acNum;
public:
    cAdjacency3d() {};
    bool readFile(std::string f, cSequence *sequence, cFrames *frames);
    double getAdjacency3d(int from, int to, int acidId);

    //void dump();
};
