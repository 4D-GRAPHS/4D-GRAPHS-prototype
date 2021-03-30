#include "sequence.h"
#include "csvreader.h"
#include "fastareader.h"

bool cSequence::readCSVFile(std::string f) {
    CSVReader reader(f);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() != 2) {
        std::cerr << "Error, malformed sequence file, must have two rows ("
            << f << ")!" << std::endl;
        return false;
    }

    if (data[0].size() != data[1].size()) {
        std::cerr << "Error, gaps scores has to be align to sequence ("
            << f << ")!" << std::endl;
        return false;
    }

    sequence = data[0];

    int i = 0;
    for (auto acid : sequence) 
        if (acidsMap.find(acid) == acidsMap.end())
            acidsMap[acid] = i++;

    for (auto s : data[1])
        gapsScore.push_back(std::stod(s));

    return true;
}

bool cSequence::readFASTAFile(std::string f, double implicitGapsScore) {
    FASTAReader reader(f);
    sequence = reader.getData();

    if (sequence.size() == 0) {
        std::cerr << "Error, malformed FASTA sequence file ("
            << f << ")!" << std::endl;
        return false;
    }

    int i = 0;
    for (auto acid : sequence) {
        if (acidsMap.find(acid) == acidsMap.end())
            acidsMap[acid] = i++;
        gapsScore.push_back(implicitGapsScore);
    }

    return true;
}

int cSequence::getAcidId(std::string acid) {
    if (acidsMap.find(acid) == acidsMap.end())
        return -1;
    else
        return acidsMap[acid];
}

std::string cSequence::getAcidName(int id) {
    for (auto a : acidsMap)
        if (a.second == id)
            return a.first;

    return "";
}

int cSequence::getProlinesNum() {
    int ret = 0;
    for (auto acid : sequence)
        if (acid == "PRO")
            ret++;

    return ret;
}

void cSequence::dump() {
    for (auto s : sequence)
        std::cout << s << " ";
    std::cout << std::endl;
    for (auto i : acidsMap)
        std::cout << i.first << ": " << i.second << std::endl;
    std::cout << std::endl;
}

