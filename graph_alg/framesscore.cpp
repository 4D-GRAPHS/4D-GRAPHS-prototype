#include "framesscore.h"
#include "csvreader.h"
#include "csvkeys.h"

bool cFramesScore::readFile(std::string file, cFrames *frames) {
    // prepare the vector
    const int f = frames->getFrames()->size();
    score.resize(f);
    for (int i = 0; i < f; i++) {
        score[i] = 0.0;
    }

    // read data from file
    CSVReader reader(file);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() == 0) {
        std::cerr << "Error, cannot read node weights score file ("
            << file << ")!" << std::endl;
        return false;
    }

    // get indices from head
    int frameIdx = -1;
    int scoreIdx = -1;
    for (int i = 0; i < data[0].size(); i++) {
        if (data[0][i] == KEY_ASG_FRAME)
            frameIdx = i;
        else if (data[0][i] == KEY_ASG_SCORE)
            scoreIdx = i;
    }
    if (frameIdx < 0 || scoreIdx < 0) {
        std::cerr << "Error, node weights miss required column ("
            << (frameIdx < 0 ? KEY_ASG_FRAME : KEY_ASG_SCORE)
            << ")!" << std::endl;
        return false;
    }

    // get data
    for (int i = 1; i < data.size(); i++) {
        int frameId = frames->getFrameIndex(data[i][frameIdx]);
        if (frameId < 0) {
            //XXX this should never happen
            std::cerr << "Error, node weights file links unknown node ("
                << data[i][frameIdx] << ")!" << std::endl;
            return false;
        }
        else {
            double weight = std::stod(data[i][scoreIdx]);
            score[frameId] = weight;
            if ((weight < 0.0) || (weight > 1.0)) {
                std::cerr << "Error, node weights file contains wrong "
                    << "value for node " << data[i][frameIdx]
                    << " (has to be between 0.0 and 1.0)!" << std::endl;
                return false;
            }
        }
    }

    // solve PRO score
    for (int i = 0; i < f; i++)
        if (! frames->getFrames()->at(i).compare(0, 3, std::string("PRO"))) 
            score[i] = 1.0;

    return true;
}

void cFramesScore::dump() {
    for (auto s : score)
        std::cout << s << " ";
    std::cout << std::endl;
}

