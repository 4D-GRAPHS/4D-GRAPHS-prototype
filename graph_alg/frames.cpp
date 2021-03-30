#include "frames.h"
#include "csvreader.h"
#include "csvkeys.h"

bool cFrames::readFile(std::string f, cSequence* const sequence) {
    CSVReader reader(f);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() == 0) {
        std::cerr << "Error, cannot read node-acid weights file ("
        << f << ")!" << std::endl;
        return false;
    }

    // get indices from head
    int frameIdx = -1;
    for (int i = 0; i < data[0].size(); i++) {
        if (data[0][i] == KEY_ASG_FRAME) {
            frameIdx = i;
            break;
        }
    }
    if (frameIdx < 0) {
        std::cerr << "Error, node-acid weights file miss required column ("
            << KEY_ASG_FRAME << ")!" << std::endl;
        return false;
    }

    // get data
    int idx = 0;
    for (int i = 1; i < data.size(); i++) {
        std::string frame = data[i][frameIdx];
        if (framesMap.find(frame) == framesMap.end()) {
            framesMap.insert({frame, idx});
            frames.push_back(frame);
            idx++;
        }
    }
    trueFrames = frames.size();

    addProlines(sequence);

    return true;
}

int cFrames::getFrameIndex(const std::string &frame) {
    if (framesMap.find(frame) == framesMap.end())
        return -1;
    else
        return framesMap[frame];
}

void cFrames::addDummyFrames(int num) {
    dummyFrames = num;
    for (int i = 0; i < num; i++) {
        std::string f = "DUMMY" + std::to_string(i+1);
        frames.push_back(f);
    }
    for (int i = frames.size()-num; i < frames.size(); i++)
        framesMap.insert({frames[i], i});
}

void cFrames::addProlines(cSequence* const sequence) {
    int proFrames = sequence->getProlinesNum();
    for (int i = 0; i < proFrames; i++) {
        std::string f = "PRO" + std::to_string(i+1);
        frames.push_back(f);
    }
    for (int i = frames.size()-proFrames; i < frames.size(); i++)
        framesMap.insert({frames[i], i});
    trueFrames += proFrames;
}

void cFrames::dump() {
    for (auto s : frames)
        std::cout << s << " ";
    std::cout << std::endl;
}

