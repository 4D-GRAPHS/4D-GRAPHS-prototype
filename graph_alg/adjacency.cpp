#include "adjacency.h"
#include "csvreader.h"
#include "csvkeys.h"

bool cAdjacency::readFile(std::string f, cFrames *frames) {
    CSVReader reader(f);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() == 0) {
        std::cerr << "Error, cannot read edge-weights file ("
            << f << ")!" << std::endl;
        return false;
    }

    // get indices from head
    int fromIdx = -1;
    int toIdx = -1;
    int weightIdx = -1;
    for (int i = 0; i < data[0].size(); i++) {
        if (data[0][i] == KEY_ADJ2D_SRC_FRAME)
            fromIdx = i;
        else if (data[0][i] == KEY_ADJ2D_DST_FRAME)
            toIdx = i;
        else if (data[0][i] == KEY_ADJ2D_SCORE)
            weightIdx = i;
    }
    if (fromIdx < 0 || toIdx < 0 || weightIdx < 0) {
        std::cerr << "Error, edge-weights file miss required column ("
            << (fromIdx < 0 ? KEY_ADJ2D_SRC_FRAME : toIdx < 0 
            ? KEY_ADJ2D_DST_FRAME : KEY_ADJ2D_SCORE) 
            << ")!" << std::endl;
        return false;
    }

    // get data
    for (int i = 1; i < data.size(); i++) {
        sAdjacency a;
        a.from = frames->getFrameIndex(data[i][fromIdx]);
        a.to = frames->getFrameIndex(data[i][toIdx]);
        if (a.from < 0 || a.to < 0) {
            std::cerr << "Error, edge-weights list links unknown node ("
                << (a.from < 0 ? data[i][fromIdx] : data[i][toIdx]) 
                << ")!" << std::endl;
            return false;
        }
        else {
            a.weight = std::stod(data[i][weightIdx]);
            adjacency.push_back(a);
            if ((a.weight < 0.0) || (a.weight > 1.0)) {
                std::cerr << "Error, edge-weights file contains wrong value "
                    << "for edge between nodes " << data[i][fromIdx] 
                    << " and " << data[i][toIdx] 
                    << " (has to be between 0.0 and 1.0)!" << std::endl;
                return false;
            }
        }
    }

    // compute ranks
    const int adjacencies = adjacency.size();
    for (int i = 0; i < adjacencies; i++) {
        adjacency[i].rank = 0;
        adjacency[i].ranked = 0;
        for (int j = 0; j < adjacencies; j++) {
            if (adjacency[i].to == adjacency[j].to) {
                adjacency[i].ranked++;
                if ((i != j) && (adjacency[i].weight <= adjacency[j].weight))
                    adjacency[i].rank++;
            }
        }
    }

    return true;
}

void cAdjacency::dump() {
    for (auto s : adjacency) 
        std::cout << s.from << "->" << s.to << ": " << s.weight 
            << " (" << s.rank << "/" << s.ranked << ")" << std::endl;
}

