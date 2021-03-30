#include "graph.h"
#include "sequence.h"
#include "frames.h"
#include "adjacency.h"
#include "adjacency3d.h"
#include "assignment.h"
#include "framesscore.h"
#include "correcthint.h"

#include <iostream>
#include <fstream>
#include <algorithm>

//////////////// Simple cmd line parsing (prefer over dependency) /////////////
char* getCmdOption(char ** begin, char ** end, const std::string & option) {
    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end)
        return *itr;
    return 0;
}

bool cmdOptionExists(char** begin, char** end, const std::string& option)
{
    return std::find(begin, end, option) != end;
}

#define CMD_SEQUENCE        "--seq"
#define CMD_EDGES           "--edge-weight"
#define CMD_RICHEDGES       "--edge-acid-weight"
#define CMD_ASSIGN          "--node-acid-weight"
#define CMD_TRUEFRAMES      "--node-weight"
#define CMD_TOCSY_ASSIGN    "--node-acid-TOCSY"
#define CMD_PATHS           "--paths"
#define CMD_OUTPUT          "--out"
#define CMD_CORRECT         "--correct"
#define CMD_DUMMIES         "--dummy-frames"
#define CMD_ZERONODE        "--zero-node"
#define CMD_ZEROEDGE        "--zero-edge"
#define CMD_OUT_FIRST       "--out-first-guess"
#define CMD_FIRST_ONLY      "--make-first-guess-only"
#define CMD_CONFLICTS_ONLY  "--count-conflicts-only"
#define CMD_DUMP_GRAPH      "--dump-graph"

void printUsage(const char* binaryName) {
    std::cerr << "usage: " << binaryName 
        << " " << CMD_SEQUENCE << " sequence.fasta "
        << CMD_EDGES << " edge_weights.csv "
        << CMD_RICHEDGES << " edge_acid_weights.csv "
        << CMD_ASSIGN << " node_acid_weights.csv "
        << "[" << CMD_TRUEFRAMES << " node_weights.csv] "
        << "[" << CMD_TOCSY_ASSIGN << " TOCSY_node_acid_weights.csv] "
        << CMD_PATHS << " paths_num "
        << "[" << CMD_DUMMIES << " dummies_num] "
        << "[" << CMD_ZERONODE << " num] "
        << "[" << CMD_ZEROEDGE << " num] "
        << CMD_OUTPUT << " output_file.csv "
        << "[" << CMD_CORRECT << " correct_path.csv] "
        << "[" << CMD_CONFLICTS_ONLY << "] "
        << "[" << CMD_DUMP_GRAPH << " prefix] "
        << std::endl;
}

int main(const int argc, char* argv[]) {
    if (! (cmdOptionExists(argv, argv+argc, CMD_SEQUENCE) && cmdOptionExists(argv, argv+argc, CMD_EDGES) && cmdOptionExists(argv, argv+argc, CMD_RICHEDGES) && cmdOptionExists(argv, argv+argc, CMD_ASSIGN) && cmdOptionExists(argv, argv+argc, CMD_PATHS) && cmdOptionExists(argv, argv+argc, CMD_OUTPUT))) {
        printUsage(argv[0]);
        return 1;
    }

///////////////////////////////// Load data ///////////////////////////////////
    cSequence sequence;
    if (! sequence.readFASTAFile(getCmdOption(argv, argv + argc, CMD_SEQUENCE)))
        return 1;
    std::cout << "Sequence loaded." << std::endl;

    cFrames frames;
    if (! frames.readFile(getCmdOption(argv, argv + argc, CMD_ASSIGN), &sequence))
        return 1;
    std::cout << "Nodes created." << std::endl;

    int useDummies = std::max(2, int(double(sequence.getSequenceLength()) / 5.0));
    if (getCmdOption(argv, argv + argc, CMD_DUMMIES)) {
        useDummies =  atoi(getCmdOption(argv, argv + argc, CMD_DUMMIES));
    }
    std::cout << "Using " << useDummies << " dummy frames." << std::endl;
    frames.addDummyFrames(useDummies);

    cAdjacency adjacency;
    if (! adjacency.readFile(getCmdOption(argv, argv + argc, CMD_EDGES), &frames))
        return 1;
    std::cout << "Edge weights loaded." << std::endl;

    cAdjacency3d adjacency3d;
    if (! adjacency3d.readFile(getCmdOption(argv, argv + argc, CMD_RICHEDGES), &sequence, &frames))
        return 1;
    std::cout << "Edge-acid weights loaded." << std::endl;

    cAssignment assignment;
    if (! assignment.readFile(getCmdOption(argv, argv + argc, CMD_ASSIGN), &frames, &sequence))
        return 1;
    std::cout << "Node-acid weights loaded." << std::endl;

    cFramesScore* trueFrames = NULL;
    char* trueFramesFile = getCmdOption(argv, argv + argc, CMD_TRUEFRAMES);
    if (trueFramesFile) {
        trueFrames = new cFramesScore();
        if (! trueFrames->readFile(trueFramesFile, &frames))
            return 1;
        std::cout << "Node weights loaded." << std::endl;
    }

    cAssignment* assignmentTOCSY = NULL;
    char* tocsyAssignmentFile = getCmdOption(argv, argv + argc, CMD_TOCSY_ASSIGN);
    if (tocsyAssignmentFile) {
        assignmentTOCSY = new cAssignment();
        if (! assignmentTOCSY->readFile(tocsyAssignmentFile, &frames, &sequence))
            return 1;
        std::cout << "TOCSY node-acid weights loaded." << std::endl;
    }

    int pathNum = atoi(getCmdOption(argv, argv + argc, CMD_PATHS));

    cCorrectHint* correct = NULL;
    char* correctFile = getCmdOption(argv, argv + argc, CMD_CORRECT);
    if (correctFile) {
        correct = new cCorrectHint;
        if (! correct->readFile(correctFile))
            return 1;
        std::cout << "Correct hint loaded." << std::endl;
    }

    double zeroNode = 0.0;
    double zeroEdge = 0.0;
    if (getCmdOption(argv, argv + argc, CMD_ZERONODE))
        zeroNode = atof(getCmdOption(argv, argv + argc, CMD_ZERONODE));
    if (getCmdOption(argv, argv + argc, CMD_ZEROEDGE))
        zeroEdge = atof(getCmdOption(argv, argv + argc, CMD_ZEROEDGE));

////////////////////////////// Build graph ////////////////////////////////////
    cGraph graphApprox;
    if (graphApprox.build(&sequence, &frames, &adjacency, &adjacency3d, &assignment, trueFrames, assignmentTOCSY, zeroNode, zeroEdge)) {
        std::cout << "Graph for approximative pathes built." << std::endl;
        if (correct) 
            graphApprox.dumpCorrectPathScore(&frames, correct);
    }
    else {
        std::cerr << "Graph build failed." << std::endl;
        return 1;
    }

    if (cmdOptionExists(argv, argv+argc, CMD_DUMP_GRAPH)) {
        std::string prefix = getCmdOption(argv, argv+argc, CMD_DUMP_GRAPH);
        std::cout << "Writing graph into " << prefix + ".dot ... ";
        std::cout.flush();
        graphApprox.dumpDOT(prefix + ".dot", &sequence, &frames);
        std::cout << "OK" << std::endl;
        std::cout << "Writing graph into " << prefix + ".csv ... ";
        std::cout.flush();
        graphApprox.dumpCSV(prefix + ".csv", &sequence, &frames);
        std::cout << "OK" << std::endl;
    }

    if (cmdOptionExists(argv, argv+argc, CMD_CONFLICTS_ONLY)) {
        int nconflicts, ndummy;
        graphApprox.getInitialPathInfo(&frames, &nconflicts, &ndummy);
        std::cout << "Number of conflicts: " << nconflicts << std::endl; 
        std::cout << "Number of dummy nodes: " << ndummy << std::endl;
        std::ofstream file(getCmdOption(argv, argv + argc, CMD_OUTPUT));
        file << "conflicts, dummy\n";
        file << nconflicts << ", " << ndummy << "\n";
        file.close();
    }
    else {
///////////////////////////// Search graph ////////////////////////////////////
        cPaths pathsApprox;
        graphApprox.approximateBestPaths(pathNum, &pathsApprox);
        std::cout << "Saving into " << getCmdOption(argv, argv + argc, CMD_OUTPUT) << "... ";
        pathsApprox.save(getCmdOption(argv, argv + argc, CMD_OUTPUT), &frames, &sequence);
        std::cout << "OK" << std::endl;
        std::cout << "Approximative paths searched." << std::endl;
        std::cout << "Best path(s):" << std::endl;
        pathsApprox.dumpSorted(&frames, &sequence, correct);
        if (pathNum > 1) {
            std::cout << "Consensual path (weighted):" << std::endl;
            pathsApprox.dumpConsensus(&frames, true, correct);
            std::cout << "Consensual path (not weighted):" << std::endl;
            pathsApprox.dumpConsensus(&frames, false, correct);
        }

#if 0
        //XXX exact searcher with duplicities, just for development purposes
        cGraph graphExact;
        if (graphExact.build(&sequence, &frames, &adjacency, &adjacency3d, &assignment, trueFrames, assignmentTOCSY, zeroNode, zeroEdge)) {
            std::cout << "Graph for exact pathes built." << std::endl;
            graphExact.dump("graphExact.dot", &sequence, &frames);
        }
        else {
            std::cerr << "Graph build failed." << std::endl;
            return 1;
        }
        cPaths pathsExact;
        graphExact.searchBestPaths(/*pathNum*/1, &pathsExact);
        std::cout << "Exact paths searched." << std::endl;
        pathsExact.dumpSorted(&frames, &sequence, correct);
#endif
    }

    if (correct) free(correct);

    return 0;
}

