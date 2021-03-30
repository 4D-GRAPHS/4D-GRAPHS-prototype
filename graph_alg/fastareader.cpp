#include "fastareader.h"

//XXX this is definitely not efficient, but who cares here...
//TODO remove whitespaces
std::vector< std::string > FASTAReader::getData()
{
    std::ifstream file(fileName);
 
    std::vector<std::string> data;
 
    std::string line = "";
    bool header = false;
    while (getline(file, line))
    {
        line.erase(std::remove(line.begin(), line.end(), '\r'), line.end()); /* remove Windows crap */
        if (line[0] == '>') {
            if (header) {
                std::cerr << "Warning, FASTA file should contain only one sequence. Ignoring following sequences.\n";
                break;
            }
            else
                header = true;
        }
        else
            for (auto ch : line) {
                switch (ch) {
                case 'A': data.push_back("ALA"); break;
                case 'B': data.push_back("ASX"); break;
                case 'C': data.push_back("CYS"); break;
                case 'D': data.push_back("ASP"); break;
                case 'E': data.push_back("GLU"); break;
                case 'F': data.push_back("PHE"); break;
                case 'G': data.push_back("GLY"); break;
                case 'H': data.push_back("HIS"); break;
                case 'I': data.push_back("ILE"); break;
                case 'K': data.push_back("LYS"); break;
                case 'L': data.push_back("LEU"); break;
                case 'M': data.push_back("MET"); break;
                case 'N': data.push_back("ASN"); break;
                case 'P': data.push_back("PRO"); break;
                case 'Q': data.push_back("GLN"); break;
                case 'R': data.push_back("ARG"); break;
                case 'S': data.push_back("SER"); break;
                case 'T': data.push_back("THR"); break;
                case 'V': data.push_back("VAL"); break;
                case 'W': data.push_back("TRP"); break;
                case 'Y': data.push_back("TYR"); break;
                case 'Z': data.push_back("GLX"); break;
                default:
                    std::cerr << "Error, FASTA file contains unknown character (" << ch << ")\n";
                    data.clear();
                    return data;
                }
            }
    }
    file.close();
 
    return data;
}

