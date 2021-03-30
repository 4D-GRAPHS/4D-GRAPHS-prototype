#include "correcthint.h"
#include "csvreader.h"
#include "csvkeys.h"

bool cCorrectHint::readFile(std::string f) {
    CSVReader reader(f);
    std::vector<std::vector<std::string>> data = reader.getData();

    if (data.size() != 1) {
        std::cerr << "Error, malformed correct hint file ("
        << f << ")!" << std::endl;
        return false;
    }

    frames = data[0];

    return true;
}

void cCorrectHint::dump() {
    for (auto s : frames)
        std::cout << s << " ";
    std::cout << std::endl;
}

