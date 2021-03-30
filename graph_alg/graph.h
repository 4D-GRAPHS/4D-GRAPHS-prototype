#pragma once

#include <limits>
#include <set>

#include "sequence.h"
#include "frames.h"
#include "adjacency.h"
#include "adjacency3d.h"
#include "assignment.h"
#include "framesscore.h"
#include "correcthint.h"

enum heuristic{
    NOREDUNDANCY,
    ALTERNATE_SUBSEQ
};

class cEdge;
class cGraph;

class cNode {
    std::vector<cEdge*> inEdges;
    std::vector<cEdge*> outEdges;
    int sequencePos;
    int frame;
    double weight;
    int rank;
    int ranked;

    double dijkstraScore;
    cEdge* dijkstraFrom;
public:
    cNode() : sequencePos(-1), frame(-1), weight(0.0), rank(0), ranked(0),
        dijkstraScore(std::numeric_limits<double>::infinity()), dijkstraFrom(NULL) {}
    cNode(const int seq, const int fr) : sequencePos(seq),rank(0), ranked(0),
        dijkstraScore(std::numeric_limits<double>::infinity()), dijkstraFrom(NULL), frame(fr), weight(0.0) {};
    void connectInEdge(cEdge* edge) {inEdges.push_back(edge);};
    void connectOutEdge(cEdge* edge) {outEdges.push_back(edge);};
    void updateWeight(const double assignment);
    void updateWeight(const double assignment, const double tfScore);
    void updateWeight(const double assignment, const double assignmentTOCSY, const double tfScore);
    void updateRank(const int rank) {this->rank = rank;};
    void updateRanked(const int ranked) {this->ranked = ranked;};
    const double getWeight() {return weight;}
    const int getRank() {return rank;};
    const int getRanked() {return ranked;};
    cEdge* getInputEdge(const int i) {return inEdges[i];};
    cEdge* getOutputEdge(const int i) {return outEdges[i];};
    std::vector<cEdge*>* getOutputEdges() {return &outEdges;};
    std::vector<cEdge*>* getInputEdges() {return &inEdges;};
    void disableOutputEdge(cNode* to);
    void enableEdges();
    int getSequencePos() {return sequencePos;};
    int getFrameId() {return frame;};

    void setAsOrigin() {dijkstraScore = 0.0; dijkstraFrom = NULL;};
    bool alterBestPath(cEdge* from);
    cEdge* getBestPathFrom() {return dijkstraFrom;};
    double getBestScore() {return dijkstraScore;};
    void clearPath();
};

class cEdge {
    double weight;
    int rank;
    int ranked;
    cNode* nodeFrom;
    cNode* nodeTo;
    bool disabled;
public:
    cEdge(cNode* from, cNode* to, double zero = 0.0);
    void updateWeight(const double edgeWeight, const double i1assignment);
    void updateRank(const int rank) {this->rank = rank;};
    void updateRanked(const int ranked) {this->ranked = ranked;};
    const double getWeight() {return weight;};
    const int getRank() {return rank;};
    const int getRanked() {return ranked;};
    cNode* getNodeFrom() {return nodeFrom;};
    cNode* getNodeTo() {return nodeTo;};
    void disable() {disabled = true;};
    void enable() {disabled = false;};
    bool isEnabled() {return !disabled;};
};

struct sPath {
    double score;
    std::vector<cNode*> path;
};

class cPaths {
    std::vector<sPath> paths;
protected:
    std::vector<sPath>* getPaths() {return &paths;};
public:
    cPaths() {};
    ~cPaths() {};
    void dumpSorted(cFrames* const frames, cSequence* const sequence, cCorrectHint* correct = NULL);
    void dumpConsensus(cFrames* const frames, bool weighted = true, cCorrectHint* correct = NULL);
    void save(std::string file, cFrames* const frames, cSequence* const sequence);

    friend cGraph;
};

class cGraph {
    cNode dummyStart;
    cNode dummyEnd;
    std::vector<std::vector<cNode*>> nodes;
    std::vector<cEdge*> edges;
    std::set<int> relevantFrames;
    static bool compareNodes(cNode* a, cNode* b);
    static bool comparePaths(sPath& a, sPath& b);
    bool usableNode(cNode* nodeCandidate, std::vector<cNode*>* const path);
    void getPath(cNode* dest, std::vector<cNode*>* path, bool reverse=true);
    double getPathScore(sPath* const path);
    bool pathConsistent(sPath* const path, std::set<cNode*>* conflicts);
    bool dijkstraNoredundant(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead);
    bool dijkstraRedundant(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead, std::vector<cNode*>* conflicts, int level = 0);
    double dijkstraRedundantFixes(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead, std::vector<cNode*>* fixes);
    bool dijkstraRedundantHeuristic(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead);
    void yenHeuristic(cNode* from, cNode* to, int maxPathes, cPaths *paths, heuristic h);
    void yen(cNode* from, cNode* to, int maxPathes, cPaths*paths);
public:
    cGraph() {};
    ~cGraph();
    bool build(cSequence* sequence, cFrames* frames, cAdjacency* adjacency, cAdjacency3d* adjacency3d, cAssignment* assignment, cFramesScore* trueFramesScore, cAssignment* assignmentTOCSY, double zeroNode = 0.0, double zeroEdge = 0.0);
    void searchBestPaths(int maxPathes, cPaths* pathes) {yen(&dummyStart, &dummyEnd, maxPathes, pathes);};
    void approximateBestPaths(int maxPathes, cPaths* pathes) {yenHeuristic(&dummyStart, &dummyEnd, maxPathes, pathes, ALTERNATE_SUBSEQ);};
    void getInitialPathInfo(cFrames* frames, int* conflicts, int* dummy);

    void dumpCorrectPathScore(cFrames* frames, cCorrectHint* correct);
    void dumpDOT(const std::string file, cSequence* sequence, cFrames* frames);
    void dumpCSV(const std::string file, cSequence* sequence, cFrames* frames);
};
