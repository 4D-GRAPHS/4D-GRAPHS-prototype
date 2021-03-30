#pragma once

#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include <algorithm>

class FASTAReader
{
    std::string fileName;
 
public:
    FASTAReader(std::string filename) :
            fileName(filename)
    { }
 
    // Function to fetch data from a CSV File
    std::vector<std::string> getData();
};

