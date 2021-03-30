#include "assignment.h"
#include "csvreader.h"
#include "csvkeys.h"

bool cAssignment::readFile(std::string file, cFrames *frames, cSequence *sequence) {
    // prepare the matrix
    const int f = frames->getFrames()->size();
    const int a = sequence->getAcidsCount();
    assignment.resize(f);
    for (int i = 0; i < f; i++) {
        assignment[i].resize(a);
        for (int j = 0; j < a; j++)
            assignment[i][j].weight = -1.0;
    }

    // read data from file
    CSVReader reader(file);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() == 0) {
        std::cerr << "Error, cannot read node-acid weights file ("
        << file << ")!" << std::endl;
        return false;
    }

    // get indices from head
    int frameIdx = -1;
    int acidIdx = -1;
    int weightIdx = -1;
    for (int i = 0; i < data[0].size(); i++) {
        if (data[0][i] == KEY_ASG_FRAME)
            frameIdx = i;
        else if (data[0][i] == KEY_ASG_ACID_NAME)
            acidIdx = i;
        else if (data[0][i] == KEY_ASG_SCORE)
            weightIdx = i;
    }
    if (frameIdx < 0 || acidIdx < 0 || weightIdx < 0) {
        std::cerr << "Error,  node-acid weights file miss required column ("
        << (frameIdx < 0 ? KEY_ASG_FRAME : acidIdx < 0 ? KEY_ASG_ACID_NAME 
        : KEY_ASG_SCORE) << ")!" << std::endl;
        return false;
    }

    // get data
    for (int i = 1; i < data.size(); i++) {
        int frameId = frames->getFrameIndex(data[i][frameIdx]);
        if (frameId < 0) {
            //XXX this should never happen
            std::cerr << "Error,  node-acid weights file links unknown node ("
            << data[i][frameIdx] << ")!" << std::endl;
            return false;
        }
        else {
            int acidId = sequence->getAcidId(data[i][acidIdx]);
            if (acidId < 0) {
                ////XXX acid is not in sequence, not a problem
            }
            else {
                double weight = std::stod(data[i][weightIdx]);
                assignment[frameId][acidId].weight = weight;
                if ((weight < 0) || (weight > 1.0)) {
                    std::cerr << "Error,  node-acid weights file contains "
                        << "wrong value for node " << data[i][frameIdx]
                        << " (has to be between 0.0 and 1.0)!" << std::endl;
                    return false;
                }
            }
        }
    }

    // solve PRO assignment
    for (int i = 0; i < f; i++)
        if (! frames->getFrames()->at(i).compare(0, 3, std::string("PRO"))) 
            //assignment[i][sequence->getAcidId("PRO")].weight = 1.0;
            for (int j = 0; j < a; j++) {
                if (sequence->getAcidName(j) == "PRO")
                    assignment[i][j].weight = 1.0;
                else
                    assignment[i][j].weight = 0.0;
            }

    // sanity check
    for (int i = 0; i < f; i++) 
        for (int j = 0; j < a; j++)
            if (assignment[i][j].weight < 0.0) {
                // ignore PRO acids and DUMMY frames
                if ((sequence->getAcidName(j) != "PRO") && (frames->getFrames()->at(i).compare(0, 5, std::string("DUMMY"))))
                    std::cerr << "Warning, node-acid weights does not cover all combinations of node + acid (node " << frames->getFrames()->at(i) << ", acid " << sequence->getAcidName(j) << ") !" << std::endl;
                assignment[i][j].weight = 0.0;
                /*return false;*/
            }

    // compute ranks
    for (int i = 0; i < f; i++) {
        for (int j = 0; j < a; j++) {
            assignment[i][j].ranked = 0;
            assignment[i][j].rank = 0;
            if (assignment[i][j].weight > 0.0) {
                for (int k = 0; k < a; k++) {
                    if (assignment[i][k].weight > 0.0) {
                        assignment[i][j].ranked++;
                        if ((j != k) && (assignment[i][k].weight >= assignment[i][j].weight))
                            assignment[i][j].rank++;
                    }
                }
            }
        }
    }

    return true;
}

void cAssignment::dump() {
    for (auto frame : assignment) {
        for (auto score : frame)
            std::cout << score.weight << " (" << score.rank << "/" << score.ranked << ") ";
        std::cout << std::endl;
    }
}

