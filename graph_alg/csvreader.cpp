#include "csvreader.h"

//XXX this is definitely not efficient, but who cares here...
//TODO remove whitespaces
std::vector<std::vector<std::string> > CSVReader::getData()
{
    std::ifstream file(fileName);
 
    std::vector<std::vector<std::string> > dataList;
 
    std::string line = "";
    while (getline(file, line))
    {
        line.erase(std::remove(line.begin(), line.end(), '\r'), line.end()); /* remove Windows crap */
        std::vector<std::string> vec;
        int pos = 0;
        std::string token;
        while ((pos = line.find(delimiter)) != std::string::npos) {
            token = line.substr(0, pos);
            int i = 0;
            while (token[i] == ' ') i++;
            int j = token.size()-1;
            while (token[j] == ' ') j--;
            vec.push_back(std::string(token.substr(i, j-i+1)));
            line.erase(0, pos + delimiter.length());
        }
        token = line;
        int i = 0;
        while (token[i] == ' ') i++;
        int j = token.size()-1;
        while (token[j] == ' ') j--;
        vec.push_back(token.substr(i, j-i+1));
        dataList.push_back(vec);
    }
    file.close();
 
    return dataList;
}

