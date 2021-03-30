#include "adjacency3d.h"
#include "csvreader.h"
#include "csvkeys.h"

bool cAdjacency3d::readFile(std::string f, cSequence *sequence, cFrames *frames) {
    frNum = frames->getTrueFramesNum();
    acNum = sequence->getAcidsCount();

    adjacency3d.resize(frNum*frNum*acNum);
    std::fill(adjacency3d.begin(), adjacency3d.end(), 0);

    CSVReader reader(f);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() == 0) {
        std::cerr << "Error, cannot read edge-acid-weight file ("
           << f << ")!" << std::endl;
        return false;
    }

    // get indices from head
    int fromIdx = -1;
    int toIdx = -1;
    int acidIdx = -1;
    int weightIdx = -1;
    for (int i = 0; i < data[0].size(); i++) {
        if (data[0][i] == KEY_ADJ3D_SRC_FRAME)
            fromIdx = i;
        else if (data[0][i] == KEY_ADJ3D_DST_FRAME)
            toIdx = i;
        else if (data[0][i] == KEY_ADJ3D_ACID_NAME)
            acidIdx = i;
        else if (data[0][i] == KEY_ADJ3D_SCORE)
            weightIdx = i;
    }
    if (fromIdx < 0 || toIdx < 0 || weightIdx < 0 || acidIdx < 0) {
        std::cerr << "Error, edge-acid-weight file miss required column ("
            << (fromIdx < 0 ? KEY_ADJ3D_SRC_FRAME : toIdx < 0 
            ? KEY_ADJ3D_DST_FRAME : weightIdx < 0 ? KEY_ADJ3D_SCORE 
            : KEY_ADJ3D_ACID_NAME)
            << ")!" << std::endl;
        return false;
    }

    // get data
    for (int i = 1; i < data.size(); i++) {
        int from = frames->getFrameIndex(data[i][fromIdx]);
        int to = frames->getFrameIndex(data[i][toIdx]);
        int acid = sequence->getAcidId(data[i][acidIdx]);
        if (from < 0 || to < 0) {
            std::cerr << "Error, edge-acid-weight file links unknown frame ("
            << (from < 0 ? data[i][fromIdx] : data[i][toIdx])
            << ")!" << std::endl;
            return false;
        }
        else {
            if (acid < 0) {
                //XXX acid is not in sequence, not a problem
            }
            else {
                double weight = std::stod(data[i][weightIdx]);
                adjacency3d[from*frNum*acNum + to*acNum + acid] = weight;
                if ((weight < 0) || (weight > 1.0)) {
                    std::cerr << "Error, edge-acid-weight file contains wrong "
                    << "value for edge between nodes " << data[i][fromIdx]
                    << " and " << data[i][toIdx] 
                    << " for acid " << data[i][acidIdx]
                    << " (has to be between 0.0 and 1.0)!" << std::endl;
                    return false;
                }
            }
        }
    }

    return true;
}

double cAdjacency3d::getAdjacency3d(int from, int to, int acidId) {
    return adjacency3d[from*frNum*acNum + to*acNum + acidId];
}

/*void cAdjacency3d::dump() {
}*/

