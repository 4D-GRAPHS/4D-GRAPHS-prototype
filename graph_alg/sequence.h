#pragma once

#include<vector>
#include<string>
#include<map>

class cSequence {
    std::vector<std::string> sequence;
    std::map<std::string, int> acidsMap;
    std::vector<double> gapsScore;
public:
    cSequence() {};
    bool readCSVFile(std::string f);
    bool readFASTAFile(std::string f, double implicitGapsScore = 0.1);
    std::vector<std::string>* getSequence() {return &sequence;};
    int getAcidId(std::string acid);
    std::string getAcidName(int acidId);
    int getAcidsCount() {return acidsMap.size();};
    double getGapsScore(int pos) {return gapsScore[pos];};
    int getProlinesNum();
    int getSequenceLength() {return sequence.size();};

    void dump();
};
