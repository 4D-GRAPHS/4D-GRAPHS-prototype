#pragma once

#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include <algorithm>

class CSVReader
{
    std::string fileName;
    std::string delimiter;
 
public:
    CSVReader(std::string filename, std::string delm = ",") :
            fileName(filename), delimiter(delm)
    { }
 
    // Function to fetch data from a CSV File
    std::vector<std::vector<std::string> > getData();
};

