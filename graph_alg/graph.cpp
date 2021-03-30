#include <iostream>
#include <fstream>
#include <assert.h>
#include <queue>
#include <functional>

#include "graph.h"
#include "statisticModel.h"

void cNode::updateWeight(const double assignment) {
    weight = StatisticModel::updateNodeWeight(weight, assignment);
}

void cNode::updateWeight(const double assignment, const double tfScore) {
    weight = StatisticModel::updateNodeWeight(weight, assignment, tfScore);
}

void cNode::updateWeight(const double assignment, const double assignmentTOCSY, const double tfScore) {
    weight = StatisticModel::updateNodeWeight(weight, assignment, assignmentTOCSY, tfScore);
}

bool cNode::alterBestPath(cEdge* from) {
    double distFrom = from->getNodeFrom()->getBestScore();
    double candidateDist = StatisticModel::addEdgeToWeight(distFrom, from);
    candidateDist = StatisticModel::addNodeToWeight(candidateDist, this);
    if (candidateDist < dijkstraScore) {
        dijkstraScore = candidateDist;
        dijkstraFrom = from;
        return true;
    }
    else
        return false;
}

void cNode::disableOutputEdge(cNode* to) {
    for (auto e : outEdges)
        if (e->getNodeTo() == to) {
            e->disable();
            return;
        }
}

void cNode::enableEdges() {
    for (auto e : outEdges)
        e->enable();
}

void cNode::clearPath() {
    dijkstraScore = std::numeric_limits<double>::infinity();
    dijkstraFrom = NULL;
}

cEdge::cEdge(cNode* from, cNode* to, double zero) {
    nodeFrom = from;
    from->connectOutEdge(this);
    nodeTo = to;
    to->connectInEdge(this);
    updateWeight(zero, zero);
    disabled = false;
    rank = 0;
    ranked = 0;
}

void cEdge::updateWeight(const double edgeWeight, const double i1assignment) {
    weight = StatisticModel::updateEdgeWeight(weight, edgeWeight, i1assignment);
}

void cPaths::dumpSorted(cFrames *frames, cSequence *sequence, cCorrectHint* correct) {
    // simple select sort, complexity is not issue here...
    const int n = paths.size();
    bool used[n];
    for (int i = 0; i < n; i++)
        used[i] = false;
    for (int i = 0; i < n; i++) {
        int bestIndex = 0;
        double best = std::numeric_limits<double>::infinity();
        for (int j = 0; j < n; j++) {
            if ((!used[j]) && (paths[j].score < best)) {
                best = paths[j].score;
                bestIndex = j;
            }
        }
        used[bestIndex] = true;
        int ok, failed, unknown;
        ok = failed = unknown = 0;
        int j = 0;
        for (auto node : paths[bestIndex].path) {
            int id = node->getFrameId();
            if (id >= 0) {
                std::cout << frames->getFrames()->at(id) << " ";
                if (correct) {
                    if (id >= frames->getTrueFramesNum()) {
                        unknown++;
                    }
                    else {
                        // PRO is compared only by a type
                        if ((sequence->getSequence()->at(j) == "PRO") && (frames->getFrames()->at(id).compare(0, 3, "PRO") == 0))
                            ok++;
                        else {
                            if (id == frames->getFrameIndex(correct->getFrames()->at(j)))
                                ok++;
                            else {
                                //std::cout << "Error at pos " << j+1 << "(frame id " << id << " " << correct->getFrames()->at(j) << ")" << std::endl;
                                failed++;
                            }
                        }
                    }
                    j++;
                }
            }
        }
        std::cout << " " << paths[bestIndex].score << std::endl;
        std::cout << "Normalised confidence scores: ";
        double scores[paths[bestIndex].path.size()-2];
        double bestScore = std::numeric_limits<double>::infinity();
        for (int n = 1; n < paths[bestIndex].path.size() - 1; n++) {
            double score = paths[bestIndex].path[n]->getWeight();
//            if (n < paths[bestIndex].path.size()-1)
                for (auto e : *(paths[bestIndex].path[n]->getOutputEdges()))
                    if (e->getNodeTo() == paths[bestIndex].path[n+1])
                        score += e->getWeight();
//            if (n > 0)
                for (auto e : *(paths[bestIndex].path[n]->getInputEdges()))
                    if (e->getNodeFrom() == paths[bestIndex].path[n-1])
                        score += e->getWeight(); 
            scores[n-1] = score;
            if (score < bestScore) bestScore = score;
        }
        for (int n = 0; n < paths[bestIndex].path.size()-2; n++)
            std::cout << bestScore/scores[n] << " ";
        std::cout << std::endl;
        if (correct)
            std::cout << "OK: " << ok << " unknown: " << unknown << " failed: " << failed << std::endl;
    }
}

void cPaths::dumpConsensus(cFrames* const frames, bool weighted, cCorrectHint* correct) {
    const int nframes = frames->getFrames()->size();
    const int pathlen = paths[0].path.size();
    const int npaths = paths.size();
    int ok, failed, unknown;
    ok = failed = unknown = 0;
    for (int i = 1; i < pathlen-1; i++) {
         //std::cout << frames->getFrames()->at(paths[0].path[f]->getFrameId()) << " ";
        double scores[nframes];
        for (int f = 0; f < nframes; f++)
            scores[f] = 0.0;
        for (int p = 0; p < npaths; p++)
            if (weighted)
                scores[paths[p].path[i]->getFrameId()] -= 1.0/paths[p].score;
            else
                scores[paths[p].path[i]->getFrameId()] -= 1.0;

        double best = std::numeric_limits<double>::infinity();
        int bestIndex= 0;
        for (int f = 0; f < nframes; f++)
            if (scores[f] < best) {
                best = scores[f];
                bestIndex = f;
            }
        std::cout << frames->getFrames()->at(bestIndex) << " ";
        if (correct) {
            if (bestIndex >= frames->getTrueFramesNum()) {
                unknown++;
            }
            else {
                if (bestIndex == frames->getFrameIndex(correct->getFrames()->at(i-1)))
                    ok++;
                else
                    failed++;
            }
        }
    }

    if (correct)
        std::cout << "OK: " << ok << " unknown: " << unknown << " failed: " << failed << std::endl;
    std::cout << std::endl;
}

void cPaths::save(std::string fileName, cFrames *frames, cSequence *sequence) {
    int best = std::numeric_limits<int>::infinity();
    for (int i = 0; i < paths.size(); i++) 
        if (paths[i].score < paths[best].score)
            best = i;

    std::ofstream file(fileName);
    file << "frame,sequence_rank\n";

    int idx = 0;
    for (auto node : paths[best].path) {
        int id = node->getFrameId();
        if (id >= 0) {
            file << frames->getFrames()->at(id) << ", " << idx << "\n";
            idx++;
        }
    }

    file.close();
}

cGraph::~cGraph() {
    for (auto column : nodes)
        for (auto node : column)
            delete node;
    for (auto edge : edges)
        delete edge;
}

bool cGraph::build(cSequence* sequence, cFrames* frames, cAdjacency* adjacency, cAdjacency3d* adjacency3d, cAssignment* assignment, cFramesScore* trueFramesScore, cAssignment* assignmentTOCSY, double zeroNode, double zeroEdge) {
    const int sequenceSize = sequence->getSequence()->size();
    const int framesCount = frames->getFrames()->size();
    const int trueFrames = frames->getTrueFramesNum();
    const int dummyFrames = frames->getDummyFramesNum();
    nodes.resize(sequenceSize);

    // iterate over sequence, create graph from left to right, layer by layer
    for (int column = 0; column < sequenceSize; column++) {
        nodes[column].resize(framesCount);
        int acidId = sequence->getAcidId(sequence->getSequence()->at(column));
        // create nodes for true frames
        int row;
        for (row = 0; row < trueFrames; row++) {
            // create node
            cNode *node = new cNode(column, row);
            if ((sequence->getSequence()->at(column) == "PRO") && (frames->getFrames()->at(row).compare(0, 3, "PRO")))
                node->updateWeight(0.0, 0.0); // at PRO parts of the sequence, non-PRO* frames have zero assignment
            else {
                double tfScore = 1.0;
                if (trueFramesScore)
                    tfScore = trueFramesScore->getScore(row);
                if ((assignmentTOCSY) && (column > 0) && (sequence->getSequence()->at(column) != "PRO")) {
                    int acidIdPredecessor = sequence->getAcidId(sequence->getSequence()->at(column-1));
                    node->updateWeight(assignment->getScore(row, acidId), assignmentTOCSY->getScore(row, acidIdPredecessor), tfScore);
                }
                else
                    node->updateWeight(assignment->getScore(row, acidId), tfScore);
            }
            //node->updateWeight(1.0 - ((double)assignment->getRank(row, acidId) / double(assignment->getRanked(row, acidId))));
            node->updateRank(assignment->getRank(row, acidId));
            node->updateRanked(assignment->getRanked(row, acidId));
            if (node->getWeight() == std::numeric_limits<double>::infinity())
                node->updateWeight(zeroNode);
            nodes[column][row] = node;

            // connect it to the graph
            if (column == 0) {
                cEdge* e = new cEdge(&dummyStart, node);
                e->updateWeight(1.0, 1.0); // dummy start is connected with w=1
                edges.push_back(e);
            }
            else
                for (int i = 0; i < framesCount; i++) {
                    if ((nodes[column-1][i]->getRanked() > 0) && (node->getRanked() > 0)) /*XXX false for DUMMY and PRO frames */
                        edges.push_back(new cEdge(nodes[column-1][i], node, zeroEdge));
                    else {
                        edges.push_back(new cEdge(nodes[column-1][i], node, sequence->getGapsScore(column-1)));
                    }
                }
        }
        // create nodes for dummy frames
        for (; row < framesCount; row++) {
            cNode *node = new cNode(column, row);
            node->updateWeight(sequence->getGapsScore(column));
            node->updateRank(0);
            node->updateRanked(0); // no rank is computed for dummy frames
            nodes[column][row] = node;

            if (column == 0) {
                cEdge* e = new cEdge(&dummyStart, node);
                e->updateWeight(1.0, 1.0); // dummy start is connected with w=1 even for dummy frames
                edges.push_back(e);
            }
            else
                for (int i = 0; i < framesCount; i++) {
                    edges.push_back(new cEdge(nodes[column-1][i], node, std::max(sequence->getGapsScore(column), sequence->getGapsScore(column-1))));
                }
        }
    }

    // connect end of the graph to the dummyEnd
    for (int row = 0; row < framesCount; row++) {
        cEdge* e = new cEdge(nodes[sequenceSize-1][row], &dummyEnd);
        e->updateWeight(1.0, 1.0); // dummy end is connected with w=1
        edges.push_back(e);
    }

#if 0
    // set edges weight according to adjacency list and i-1 assignment
    for (auto adj : *(adjacency->getAdjacency())) {
        cEdge *e;
        for (int i = 0; i < sequenceSize-1; i++) {
            e = nodes[i][adj.from]->getOutputEdge(adj.to);
            assert(e->getNodeFrom() == nodes[i][adj.from]);
            assert(e->getNodeTo() == nodes[i+1][adj.to]);
/*            if ((sequence->getSequence()->at(i) == "PRO") || (sequence->getSequence()->at(i+1) == "PRO")) {
                e->updateWeight(adj.weight, 1.0); // do nothing, we are at PRO frame
            }*/
            if (sequence->getSequence()->at(i+1) == "PRO") {
                e->updateWeight(adj.weight, 1.0); // do nothing, we don't have assignment for PRO frame
            }
            else {
                int i1acidId = sequence->getAcidId(sequence->getSequence()->at(i));
                e->updateWeight(adj.weight, assignment->getScore(adj.to, i1acidId));
            }
            e->updateRank(adj.rank);
            e->updateRanked(adj.ranked);
        }
    }
#endif
#if 1
    // set edges weight according to adjacency and 3D adjacency list with scores
    for (auto adj : *(adjacency->getAdjacency())) {
        cEdge *e;
        for (int i = 0; i < sequenceSize-1; i++) {
            e = nodes[i][adj.from]->getOutputEdge(adj.to);
            assert(e->getNodeFrom() == nodes[i][adj.from]);
            assert(e->getNodeTo() == nodes[i+1][adj.to]);
            //e->updateWeight(1.0 - ((double)adj.rank / (double)adj.ranked));
            if ((sequence->getSequence()->at(i) == "PRO") || (sequence->getSequence()->at(i+1) == "PRO")) {
                e->updateWeight(adj.weight, 1.0);
            }
            else {
                e->updateWeight(adj.weight, adjacency3d->getAdjacency3d(adj.from, adj.to, sequence->getAcidId(sequence->getSequence()->at(i))));
            }
            e->updateRank(adj.rank);
            e->updateRanked(adj.ranked);
        }
    }
#endif
#if 0
    // set edges weight according to adjacency and 3D adjacency list with nums
    for (auto adj : *(adjacency->getAdjacency())) {
        cEdge *e;
        for (int i = 0; i < sequenceSize-1; i++) {
            e = nodes[i][adj.from]->getOutputEdge(adj.to);
            assert(e->getNodeFrom() == nodes[i][adj.from]);
            assert(e->getNodeTo() == nodes[i+1][adj.to]);
            //e->updateWeight(1.0 - ((double)adj.rank / (double)adj.ranked));
            if ((sequence->getSequence()->at(i) == "PRO") || (sequence->getSequence()->at(i+1) == "PRO")) {
                e->updateWeight(adj.weight, 1.0);
            }
            else {
                std::string acid = sequence->getSequence()->at(i);
                double peaks = adjacency3d->getAdjacency3d(adj.from, adj.to, sequence->getAcidId(acid));
                double score;
                if (acid == "ALA")
                    score = peaks/2.0;
                else if (acid == "ARG")
                    score = peaks/4.0;
                else if (acid == "ASN")
                    score = peaks/2.0;
                else if (acid == "ASP")
                    score = peaks/2.0;
                else if (acid == "CYS")
                    score = peaks/2.0;
                else if (acid == "GLN")
                    score = peaks/3.0;
                else if (acid == "GLU")
                    score = peaks/3.0;
                else if (acid == "GLY")
                    score = peaks/1.0;
                else if (acid == "HIS")
                    score = peaks/2.0;
                else if (acid == "ILE")
                    score = peaks/5.0;
                else if (acid == "LEU")
                    score = peaks/4.0;
                else if (acid == "LYS")
                    score = peaks/5.0;
                else if (acid == "MET")
                    score = peaks/4.0;
                else if (acid == "PHE")
                    score = peaks/2.0;
                else if (acid == "PRO")
                    score = peaks/4.0; //XXX currently we don't solve PRO here
                else if (acid == "SER")
                    score = peaks/2.0;
                else if (acid == "THR")
                    score = peaks/3.0;
                else if (acid == "TRP")
                    score = peaks/2.0;
                else if (acid == "TYR")
                    score = peaks/2.0;
                else if (acid == "VAL")
                    score = peaks/3.0;
                else
                    std::cerr << "Terrible thing happen, unknown acid!" << std::endl;
                e->updateWeight(adj.weight, score);
            }
            e->updateRank(adj.rank);
            e->updateRanked(adj.ranked);
        }
    }
#endif

    // handle edges to/from prolines
    for (int i = 0; i < sequenceSize-1; i++) {
        if (sequence->getSequence()->at(i) == "PRO") {
            for (auto n : nodes[i]) {
                if (0 == frames->getFrames()->at(n->getFrameId()).compare(0,3,"PRO")) {
                    for (auto e : *(n->getOutputEdges())) {
                        if (e->getNodeTo()->getRanked() > 0) {
/*                            std::cout << frames->getFrames()->at(n->getFrameId())
                                << " -> "
                                << frames->getFrames()->at(e->getNodeTo()->getFrameId())
                                << ": " << assignment->getScore(e->getNodeTo()->getFrameId(), sequence->getAcidId("PRO"))
                                << std::endl;*/
                            e->updateWeight(1.0, assignment->getScore(e->getNodeTo()->getFrameId(), sequence->getAcidId("PRO")));
                        }
                    }
                    for (auto e : *(n->getInputEdges())) {
                        if (e->getNodeFrom()->getRanked() > 0) {
/*                            std::cout << frames->getFrames()->at(n->getFrameId())
                                << " -> "
                                << frames->getFrames()->at(e->getNodeTo()->getFrameId())
                                << ": " << assignment->getScore(e->getNodeTo()->getFrameId(), sequence->getAcidId("PRO"))
                                << std::endl;*/
                            e->updateWeight(1.0, assignment->getScore(e->getNodeFrom()->getFrameId(), sequence->getAcidId("PRO")));
                        }
                    }
                }
            }
        }
    }


    // collect set of reachable nodes
    if (nodes.size() > 1) {
        std::set<int> allFrames;
        for (int i = 0; i < nodes[0].size(); i++)
            allFrames.insert(i);
        while (! allFrames.empty()) {
            std::set<int> mySet;
            mySet.insert(*(allFrames.begin()));
            allFrames.erase(allFrames.begin());
            bool newInsertion;
            do {
                for (auto myFrame : mySet) {
                    newInsertion = false;
                    for (auto f : allFrames) {
                        bool connected = false;
                        for (auto e : *(nodes[1][f]->getOutputEdges()))
                            if ((e->getNodeTo()->getFrameId() == myFrame)
                                && (e->getWeight() < std::numeric_limits<double>::infinity())) {
                                connected = true;
                                break;
                            }
                        //XXX the second loop is probably not necessary, but who knows
                        //XXX if this is symmetric...
                        for (auto e : *(nodes[1][f]->getInputEdges()))
                            if ((e->getNodeFrom()->getFrameId() == myFrame)
                                && (e->getWeight() < std::numeric_limits<double>::infinity())) {
                                connected = true;
                                break;
                            }
                        if (connected) {
                            mySet.insert(f);
                            newInsertion = true;
                        }
                    }
                }
                for (auto f : mySet) {
                    allFrames.erase(f);
                }
            } while (newInsertion);
            if (mySet.size() >= nodes.size())
                relevantFrames.insert(mySet.begin(), mySet.end());
        }
    }
    else {
        for (int i = 0; i < nodes[0].size(); i++)
            relevantFrames.insert(i);
    }

    if (relevantFrames.empty()) {
        std::cerr << "Error, adjacency list does not allow to cover the whole sequence." << std::endl;
        return false;
    }
    else {
        return true;
    }
}

bool cGraph::compareNodes(cNode* a, cNode* b) {
    return (b->getBestScore() < a->getBestScore());
}

bool cGraph::comparePaths(sPath& a, sPath& b) {
    return (b.score < a.score);
}

void cGraph::getPath(cNode* dest, std::vector<cNode*>* path, bool reverse) {
    path->clear();

    cNode* n = dest;

    while (n->getBestPathFrom() != NULL) {
        path->push_back(n);
        n = n->getBestPathFrom()->getNodeFrom();
    }
    path->push_back(n);

    if (reverse) {
        int size = path->size();
        for (int i = 0; i < size/2; i++) {
            cNode* tmp = (*path)[i];
            (*path)[i] = (*path)[size-1-i];
            (*path)[size-1-i] = tmp;
        }
    }
}

double cGraph::getPathScore(sPath* const path) {
    double score = 0.0;
    int size = path->path.size();
    if (size == 0)
        return score;
    if (size == 1)
        return path->path[0]->getWeight();
    for (int i = 0; i < path->path.size(); i++) {
        score = StatisticModel::addNodeToWeight(score, path->path[i]);
    }
    for (int i = 0; i < path->path.size()-1; i++) {
        for (auto e : *(path->path[i]->getOutputEdges()))
            if (e->getNodeTo() == path->path[i+1])
                score = StatisticModel::addEdgeToWeight(score, e);
    }
    return score;
}

bool cGraph::pathConsistent(sPath* const path, std::set<cNode*>* conflicts) {
    conflicts->clear();
    for (int i = path->path.size()-1; i >= 0; i--)
        for (int j = i-1; j >= 0; j--)
            if ((j != i) && (path->path[i]->getFrameId() != -1) && (path->path[i]->getFrameId() == path->path[j]->getFrameId())) {
                conflicts->insert(path->path[i]);
                conflicts->insert(path->path[j]);
            }
    if (conflicts->size() > 0)
        return false;
    else
        return true;
}

bool cGraph::usableNode(cNode* nodeCandidate, std::vector<cNode*>* const path){
    if (nodeCandidate->getFrameId() == -1)
        return true;
    if (nodeCandidate->getWeight() == std::numeric_limits<double>::infinity())
        return false; //XXX we do not include nodes with zero weight
    for (auto n : *path)
        if ((n != nodeCandidate) && (n != NULL)
            && (nodeCandidate->getFrameId() == n->getFrameId()))
            return false;
    return true;
}

bool cGraph::dijkstraNoredundant(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead) {
    // clear structures and build the queue
    path->path.clear();
    from->setAsOrigin();
    std::priority_queue<cNode*, std::vector<cNode*>, std::function<bool(cNode*, cNode*)>> nodesQueue(cGraph::compareNodes);
    const int startFrom = from->getSequencePos() + 1;
    for (int column = startFrom; column < nodes.size(); column++)
        for (auto vertex : nodes[column]) 
            vertex->clearPath();
    nodesQueue.push(from);
    if (to->getSequencePos() == -1) 
        to->clearPath();

    // empty queue seeking for the best path
    std::vector<cNode*> partialPath;
    while (!nodesQueue.empty()) {
        cNode* n = nodesQueue.top();

        //std::cout << "Enqueuing node (" << n->getSequencePos() << ", " << n->getFrameId() << ")" << std::endl;

        if (n == to)
            break;

        nodesQueue.pop();
        getPath(n, &partialPath, false);
        partialPath.insert(partialPath.end(), fixedHead->begin(), fixedHead->end());
        if (usableNode(n, &partialPath))
            for (auto edge : *(n->getOutputEdges()))
                if (edge->getWeight() < std::numeric_limits<double>::infinity() && edge->isEnabled() && usableNode(edge->getNodeTo(), &partialPath)) {
                    bool x = edge->getNodeTo()->alterBestPath(edge);
                    //if (x)
                    //    std::cout << "Path (" << edge->getNodeFrom()->getSequencePos() << ", " << edge->getNodeFrom()->getFrameId() << ") -> (" << edge->getNodeTo()->getSequencePos() << ", " << edge->getNodeTo()->getFrameId() << ") improved" << std::endl;
                    if (x)
                        nodesQueue.push(edge->getNodeTo());
                }
    }

    getPath(to, &(path->path));
    path->score = to->getBestScore();

    if (path->score == std::numeric_limits<double>::infinity())
        return false;
    else
        return true;
}

bool cGraph::dijkstraRedundant(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead, std::vector<cNode*>* conflicts, int level) {
    // clear structures and build the queue
    path->path.clear();
    from->setAsOrigin();
    std::priority_queue<cNode*, std::vector<cNode*>, std::function<bool(cNode*, cNode*)>> nodesQueue(cGraph::compareNodes);
    const int startFrom = from->getSequencePos() + 1;
    for (int column = startFrom; column < nodes.size(); column++)
        for (auto vertex : nodes[column])
            vertex->clearPath();
    nodesQueue.push(from);
    if (to->getSequencePos() == -1)
        to->clearPath();

    //std::cout << conflicts->size() << " ";
    if (conflicts->size() >= nodes.size()*nodes[0].size())
        return false; // we cannot search anymore

    // empty queue seeking for the best path
    while (!nodesQueue.empty()) {
        cNode* n = nodesQueue.top();

        //std::cout << "Enqueuing node (" << n->getSequencePos() << ", " << n->getFrameId() << ")" << std::endl;

        if (n == to)
            break;

        nodesQueue.pop();
        
        if (usableNode(n, fixedHead)  
            && ((n->getSequencePos() == -1) || (relevantFrames.find(n->getFrameId()) != relevantFrames.end())))
            for (auto edge : *(n->getOutputEdges()))
                if (edge->getWeight() < std::numeric_limits<double>::infinity() && edge->isEnabled() && usableNode(edge->getNodeTo(), fixedHead)) {
                    bool allowed = true;
                    for (auto c : *conflicts)
                        if (edge->getNodeTo() == c) {
                            allowed = false;
                            break;
                        }
                    if (allowed) {
                        bool x = edge->getNodeTo()->alterBestPath(edge);
                        //if (x)
                            //std::cout << "Path (" << edge->getNodeFrom()->getSequencePos() << ", " << edge->getNodeFrom()->getFrameId() << ") -> (" << edge->getNodeTo()->getSequencePos() << ", " << edge->getNodeTo()->getFrameId() << ") improved: " << edge->getNodeTo()->getBestScore() << std::endl;
                        if (x)
                            nodesQueue.push(edge->getNodeTo());
                    }
                }
    }

    getPath(to, &(path->path));
    path->score = to->getBestScore();
    if (path->score == std::numeric_limits<double>::infinity())
        return false; // Path not found


return true;
    /*std::cout << "Have path ";
    for (auto n : path->path)
        std::cout << n->getFrameId() << " ";
    std::cout << std::endl;*/

    std::set<cNode*> myConflicts;
    sPath pathCandidate;
    if (! pathConsistent(path, &myConflicts)) {
        path->score = -1.0;
        int i = 0;
        for (auto c : myConflicts) {
            bool haveIt = false;
            for (auto co : *conflicts)
                if (co == c) {
                    haveIt = true;
                    break;
                }
            if (haveIt)
                continue;
            if (level < 3)
                std::cout << "Level " << level << " iter " << i << "/" << myConflicts.size() << std::endl; 
            std::vector<cNode*> newConflicts = *conflicts;
            newConflicts.push_back(c);
            /*std::cout << "Altering path, conflicts: ";
            for (auto c : newConflicts)
                std::cout << "(" << c->getSequencePos() << ", " << c->getFrameId() << ") ";
            std::cout << std::endl;*/
            if (dijkstraRedundant(from, to, &pathCandidate, fixedHead, &newConflicts, level+1)) {
                //std::cout << "Path found, score " << pathCandidate.score << std::endl;
                if (pathCandidate.score > path->score) {
                    //std::cout << "Path has been accepted.\n";
                    //std::cout << "Consistent path FOUND." << std::endl;
                    //for (auto c : pathCandidate.path)
                    //    std::cout << "(" << c->getSequencePos() << ", " << c->getFrameId() << ") ";
                    //std::cout << std::endl;
                    path->score = pathCandidate.score;
                    path->path = pathCandidate.path;
                    //std::cout << "Path score improved: " << path->score << std::endl;
                }
            }   
            i++;
        }
        if (path->score < std::numeric_limits<double>::infinity()) {
            //std::cout << "Path OK." << std::endl;
            return true;
        }
        else {
            //std::cout << "Path FAILED." << std::endl;
            return false;
        }
    }
    else {
        //std::cout << "Consistent path found with score: " << path->score << std::endl;
        //std::cout << "Path OK 2." << std::endl;
        return true;
    }
}

double cGraph::dijkstraRedundantFixes(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead, std::vector<cNode*>* fixes) {
    // clear structures and build the queue
    path->path.clear();
    from->setAsOrigin();
    std::priority_queue<cNode*, std::vector<cNode*>, std::function<bool(cNode*, cNode*)>> nodesQueue(cGraph::compareNodes);
    const int startFrom = from->getSequencePos() + 1;
    for (int column = startFrom; column < nodes.size(); column++)
        for (auto vertex : nodes[column])
            vertex->clearPath();
    nodesQueue.push(from);
    if (to->getSequencePos() == -1)
        to->clearPath();

    // empty queue seeking for the best path
    while (!nodesQueue.empty()) {
        cNode* n = nodesQueue.top();

        if (n == to)
            break;

        nodesQueue.pop();

        //if (usableNode(n, fixedHead)
        //    && ((n->getSequencePos() == -1) || (relevantFrames.find(n->getFrameId()) != relevantFrames.end()))) {
            for (auto edge : *(n->getOutputEdges())) {
                if (edge->getWeight() < std::numeric_limits<double>::infinity() && edge->isEnabled() && usableNode(edge->getNodeTo(), fixedHead)) {
                    if ((edge->getNodeTo()->getSequencePos() != -1) && (fixes->at(edge->getNodeTo()->getSequencePos()) != NULL)) {
                        if (fixes->at(edge->getNodeTo()->getSequencePos()) == edge->getNodeTo() && (edge->getNodeTo()->alterBestPath(edge)))
                            nodesQueue.push(edge->getNodeTo());
                    }
                    else {
                        if (usableNode(edge->getNodeTo(), fixes) && (edge->getNodeTo()->alterBestPath(edge)))
                            nodesQueue.push(edge->getNodeTo());
                    }
                }
            }
        
    }

    getPath(to, &(path->path));
    path->score = to->getBestScore();
    return path->score;
}

void cGraph::getInitialPathInfo(cFrames* frames, int* conflicts, int* dummy) {
    std::vector<cNode*> fixes;
    for (int i = 0; i < nodes.size(); i++)
        fixes.push_back(NULL);     // no fixes
    std::vector<cNode*> fixedHead; // void vector
    sPath pathCandidate;
    dijkstraRedundantFixes(&dummyStart, &dummyEnd, &pathCandidate, &fixedHead, &fixes);

    std::set<cNode*> myConflicts;
    pathConsistent(&pathCandidate, &myConflicts);
    *conflicts = myConflicts.size();

    *dummy = 0;
    for (auto n: pathCandidate.path) {
        int fid = n->getFrameId();
        if (fid >= 0) {
            if (0 == frames->getFrames()->at(fid).compare(0,5,"DUMMY")) 
                (*dummy)++;
        }
    }
}


bool cGraph::dijkstraRedundantHeuristic(cNode* from, cNode* to, sPath* path, std::vector<cNode*>* fixedHead) {
    std::vector<cNode*> fixes;
    for (int i = 0; i < nodes.size(); i++)
        fixes.push_back(NULL);

    sPath pathCandidate;
    int nconflicts;
    do {
        // search path, potentially with conflict
        double scoreOrig = dijkstraRedundantFixes(from, to, &pathCandidate, fixedHead, &fixes);

        // locate conflicts
        std::set<cNode*> myConflicts;
        pathConsistent(&pathCandidate, &myConflicts);
        nconflicts = myConflicts.size();

        int fix = 0;
        for (auto n : fixes)
            if (n) fix++;

        std::cout << "Have " << nconflicts << " conflicts (score " << scoreOrig << ", fixed nodes " << fix << ")\n";
        /*for (auto n : pathCandidate.path)
            std::cout << n->getFrameId() << " ";
        std::cout << std::endl;*/

        ////////////////////////////////////
        /*const int frames = nodes[0].size();
        for (auto c : myConflicts) {
            cNode *tmp = pathCandidate.path[c->getSequencePos()+1];
            pathCandidate.path[c->getSequencePos()+1] = nodes[c->getSequencePos()][frames-1];
            double altS = getPathScore(&pathCandidate);
            pathCandidate.path[c->getSequencePos()+1] = tmp;
            std::cout << "Penalty for (" << c->getSequencePos() << "," 
                << c->getFrameId() << "): " << s - altS << std::endl;
        }*/
        /////////////////////////////////////

        std::vector<std::vector<cNode*>> subsequences;
        double bestSSScore = std::numeric_limits<double>::infinity();
        int bestSSIndex = -1;
        for (int i = 0; i < pathCandidate.path.size(); i++)  {
            // is in conflict?
            if (myConflicts.find(pathCandidate.path[i]) != myConflicts.end()) {
                std::vector<cNode*> ss;
                ss.push_back(pathCandidate.path[i]);
                for (int j = i+1; j < pathCandidate.path.size(); j++) {
                    if (myConflicts.find(pathCandidate.path[j]) != myConflicts.end()) {
                        bool innerConflict = false;
                        for (auto n : ss)
                            if (n->getFrameId() == pathCandidate.path[j]->getFrameId())
                                innerConflict = true;
                        if (! innerConflict) {
                            ss.push_back(pathCandidate.path[j]);
                            i++;
                        }
                        else
                            break;
                    }
                    else
                        break;
                }
                // check if sequence collides with from node
                bool hasFrom = false;
                for (auto n : ss)
                    if (n->getFrameId() == from->getFrameId()) {
                        hasFrom = true;
                        break;
                    }
                if (! hasFrom) {
                    subsequences.push_back(ss);
                    for (auto n : ss) {
                    //std::cout << "(" << n->getSequencePos() << "," << n->getFrameId() << ") : ";
                        fixes[n->getSequencePos()] = n;
                    }
                    sPath alternatePath;
                    double score = dijkstraRedundantFixes(from, to, &alternatePath, fixedHead, &fixes);
                    //std::cout << score << std::endl;
                    for (auto n : ss) {
                        fixes[n->getSequencePos()] = NULL;
                    }
                    if (score < bestSSScore) {
                        bestSSScore = score;
                        bestSSIndex = subsequences.size()-1;
                    }
                }
            }
        }

        if (nconflicts) {
            if (bestSSIndex > -1) {
                std::cout << "Fixing subsekvence " << bestSSIndex << " with score "
                    << bestSSScore << std::endl;
                for (auto n : subsequences[bestSSIndex]) {
                    fixes[n->getSequencePos()] = n;
                    std::cout << "(" << n->getSequencePos() << "," << n->getFrameId() << ") ";
                }
                std::cout << std::endl;
            }
            else {
                std::cout << "Cannot fix subsekvence" << std::endl;
                sPath alternatePath;
                dijkstraNoredundant(from, to, &alternatePath, fixedHead);
                nconflicts = 0;
            }
        }

        /////////////////////////////////////

        /*if (nconflicts > 0) {
            // fix the node with minimal impact on score
            double bestScore = 0.0;
            cNode* bestToFix = NULL;
            for (auto c : myConflicts) {
                fixes[c->getSequencePos()] = c;
                double score = dijkstraRedundantFixes(from, to, &pathCandidate, fixedHead, &fixes);
                fixes[c->getSequencePos()] = NULL;
                if (score > bestScore) {
                    bestScore = score;
                    bestToFix = c;
                }
            }
            fixes[bestToFix->getSequencePos()] = bestToFix;
            std::cout << "Fixing (" << bestToFix->getSequencePos() << "," << 
                bestToFix->getFrameId() << ")\n";
        }*/
    } while (nconflicts > 0);

    getPath(to, &(path->path));
    path->score = to->getBestScore();
    return (path->score < std::numeric_limits<double>::infinity());
}

void cGraph::yenHeuristic(cNode* from, cNode* to, int maxPathes, cPaths* paths, heuristic h) {
    sPath path;
    std::priority_queue<sPath, std::vector<sPath>, std::function<bool(sPath&, sPath&)>> pathsQueue(cGraph::comparePaths);
    std::vector<sPath> enqueued;
   
    std::vector<cNode*> voidVector; 
    switch (h) {
    case NOREDUNDANCY:
        dijkstraNoredundant(from, to, &path, &voidVector);
        break;
    case ALTERNATE_SUBSEQ:
        dijkstraRedundantHeuristic(from, to, &path, &voidVector);
        break;
    default:
        std::cerr << "ERROR: Unknown heuristic." << std::endl;
        break;
    }
    
    paths->getPaths()->clear();
    paths->getPaths()->push_back(path);

    for (int k = 1; k < maxPathes; k++) {
        // iterate over spur nodes
        for (int i = 0; i < (*paths->getPaths())[0].path.size() - 2; i++) {
            // get spur node and root path
            cNode* spurNode = (*paths->getPaths())[k-1].path[i];
            std::vector<cNode*>::const_iterator fromIt = (*paths->getPaths())[k-1].path.begin();
            std::vector<cNode*>::const_iterator toIt = (*paths->getPaths())[k-1].path.begin() + i;
            std::vector<cNode*> rootPath(fromIt, toIt);
            // eliminate edges
            for (int j = 0; j < paths->getPaths()->size(); j++) {
                std::vector<cNode*>::const_iterator fromIt = (*paths->getPaths())[j].path.begin();
                std::vector<cNode*>::const_iterator toIt = (*paths->getPaths())[j].path.begin() + i;
                std::vector<cNode*> rootPathOverlay(fromIt, toIt);
                if (rootPath == rootPathOverlay)
                    (*paths->getPaths())[j].path[i]->disableOutputEdge((*paths->getPaths())[j].path[i+1]);
            }
            // construct the path
            sPath spurPath;
            std::vector<cNode*> forbiddenPath = rootPath;
            switch (h) {
            case NOREDUNDANCY:
                dijkstraNoredundant(spurNode, to, &spurPath, &(forbiddenPath));
                break;
            case ALTERNATE_SUBSEQ:
                dijkstraRedundantHeuristic(spurNode, to, &spurPath, &(forbiddenPath));
                break;
            }
            if (to->getBestScore() < std::numeric_limits<double>::infinity()) {
                sPath totalPath;
                totalPath.path = rootPath;
                totalPath.path.insert(totalPath.path.end(), spurPath.path.begin(), spurPath.path.end()); 
                totalPath.score = getPathScore(&totalPath);
                // check if unique
                bool unique = true;
                for (auto p : enqueued) {
                    bool ok = false;
                    for (int i = totalPath.path.size()-1; i > 0; i--)
                        if ((totalPath.path[i] != p.path[i]) && (p.path[i]->getRanked() != 0)) {
                            ok = true;
                            break;
                        }
                    if (! ok) {
                        unique = false;
                        break;
                    }
                }
                if (unique) {
                    //std::cout << "Unique " << totalPath.score << std::endl;
                    pathsQueue.push(totalPath);
                    enqueued.push_back(totalPath);
                    std::cout << "Paths in queue: " << pathsQueue.size() 
                        << "(" << enqueued.size() << ")\n";
                }
            }
            // restore edges
            for (int j = 0; j < paths->getPaths()->size(); j++)
                (*paths->getPaths())[j].path[i]->enableEdges();
        }

        if (pathsQueue.empty())
            break;

        paths->getPaths()->push_back(pathsQueue.top());
        pathsQueue.pop();
    }
}

void cGraph::yen(cNode* from, cNode* to, int maxPathes, cPaths* paths) {
    sPath path;
    std::priority_queue<sPath, std::vector<sPath>, std::function<bool(sPath&, sPath&)>> pathsQueue(cGraph::comparePaths);
    std::vector<sPath> enqueued;
   
    std::vector<cNode*> conflicts;
    std::vector<cNode*> voidRoot;
    //std::cout << "Initial dijkstra BEGIN" << std::endl;
    dijkstraRedundant(from, to, &path, &voidRoot, &conflicts);
    //std::cout << "Initial dijkstra END" << std::endl;
    paths->getPaths()->clear();
    paths->getPaths()->push_back(path);

    for (int k = 1; k < maxPathes; k++) {
        //std::cout << "k=" << k << std::endl;
        // iterate over spur nodes
        for (int i = 0; i < (*paths->getPaths())[0].path.size() - 2; i++) {
            //std::cout << "i=" << i << std::endl;
            // get spur node and root path
            cNode* spurNode = (*paths->getPaths())[k-1].path[i];
            std::vector<cNode*>::const_iterator fromIt = (*paths->getPaths())[k-1].path.begin();
            std::vector<cNode*>::const_iterator toIt = (*paths->getPaths())[k-1].path.begin() + i;
            std::vector<cNode*> rootPath(fromIt, toIt);
            // eliminate edges
            for (int j = 0; j < paths->getPaths()->size(); j++) {
                std::vector<cNode*>::const_iterator fromIt = (*paths->getPaths())[j].path.begin();
                std::vector<cNode*>::const_iterator toIt = (*paths->getPaths())[j].path.begin() + i;
                std::vector<cNode*> rootPathOverlay(fromIt, toIt);
                if (rootPath == rootPathOverlay)
                    (*paths->getPaths())[j].path[i]->disableOutputEdge((*paths->getPaths())[j].path[i+1]);
            }
            // construct the path
            sPath spurPath;
            std::vector<cNode*> conflicts;
            std::vector<cNode*> forbiddenPath = rootPath;
            bool ok = dijkstraRedundant(spurNode, to, &spurPath, &forbiddenPath, &conflicts);
            if (ok && spurPath.score < std::numeric_limits<double>::infinity()) {
                //std::cout << "Path FOUND\n";
                sPath totalPath;
                totalPath.path = rootPath;
                totalPath.path.insert(totalPath.path.end(), spurPath.path.begin(), spurPath.path.end()); 
                totalPath.score = getPathScore(&totalPath);
                // check if consistent
                //if (pathConsistent(&totalPath)) {
                    // check if unique
                    bool unique = true;
                    for (auto p : enqueued)
                        if (p.path == totalPath.path) {
                            unique = false;
                            break;
                    }
                    if (unique) {
                        //std::cout << "Unique " << totalPath.score << std::endl;
                        pathsQueue.push(totalPath);
                        enqueued.push_back(totalPath);
                    }
                //}
            }
            // restore edges
            for (int j = 0; j < paths->getPaths()->size(); j++)
                (*paths->getPaths())[j].path[i]->enableEdges();
        }

        if (pathsQueue.empty())
            break;

        paths->getPaths()->push_back(pathsQueue.top());
        pathsQueue.pop();
    }
}

void cGraph::dumpCorrectPathScore(cFrames* frames, cCorrectHint* correct) {
    double score = 0.0;

    std::cout << "Best path: ";
    for (int i = 0; i < correct->getFrames()->size(); i++) {
        for (auto n : nodes[i]) {
            if (n->getFrameId() == frames->getFrameIndex(correct->getFrames()->at(i))) {
                std::cout << "*" << n->getWeight() << "("
                    << frames->getFrames()->at(n->getFrameId()) << ": "
                    << n->getRank() << "/" << n->getRanked() << ")";
                score = StatisticModel::addNodeToWeight(score, n);
                //std::cout << n->getFrameId() << " ";
                if (i < correct->getFrames()->size()-1) {
                    for (auto n2 : nodes[i+1])
                        if (n2->getFrameId() == frames->getFrameIndex(correct->getFrames()->at(i+1))) {
                            for (auto e : *(n->getOutputEdges()))
                                if (e->getNodeTo() == n2) {
                                   score = StatisticModel::addEdgeToWeight(score, e);
                                    std::cout << "*" << e->getWeight();
                                    std::cout << "(" << e->getRank() << "/" << e->getRanked() << ")";
                                }
                            break;
                        }
                }
            }
        }
    }
    std::cout << std::endl;

    std::cout << "Score of the correct path: " << score << std::endl;
}


void cGraph::dumpDOT(const std::string file, cSequence* sequence, cFrames* frames) {
    const int sequenceSize = sequence->getSequence()->size();
    const int framesCount = frames->getFrames()->size();

    std::ofstream out;
    out.open(file);
    out << "digraph {\nrankdir=LR;\n";

    // create sequence
    for (int column = 0; column < sequenceSize; column++)
        out << column << "[label = \"" << sequence->getSequence()->at(column)
            << "\", color = red];" << std::endl;

    // create vertices
    for (int column = 0; column < sequenceSize; column++)
        for (int row = 0; row < framesCount; row++)
            out << column << "." << row << "[label = \"" 
                << frames->getFrames()->at(row) <<  "\", color = \"0.0 0.1 " 
                << 1.0-nodes[column][row]->getWeight() << "\"];" <<std::endl;

    
    // create edges
    for (int column = 1; column < sequenceSize; column++)
        for (int row = 0; row < framesCount; row++)
            for (int edge = 0; edge < framesCount; edge++)   
                out << column-1 << "." << row << " -> "
                    << column << "." << edge << "[color = \"0.0 0.1 "
                    << 1.0-nodes[column-1][row]->getOutputEdge(edge)->getWeight()
                    << "\"];" << std::endl;

    // create layers
    for (int column = 0; column < sequenceSize; column++) {
        out << "{ rank=same; " << column << ", ";
        for (int row = 0; row < framesCount-1; row++)
            out << column << "." << row << ", ";
        out << column << "." << framesCount-1;
        out << "}" << std::endl;
    }
    out << "}\n";
    out.close();
}

void cGraph::dumpCSV(const std::string file, cSequence* sequence, cFrames* frames) {
    const int sequenceSize = sequence->getSequence()->size();
    const int framesCount = frames->getFrames()->size();

    std::ofstream out;
    out.open(file);

    out << "sequence_pos,source_frame,target_frame,node_weight,edge_weight,weight\n";

    for (int seq = 1; seq < sequenceSize; seq++)
        for (int from = 0; from < framesCount; from++)
            for (int to = 0; to < framesCount; to++) {
                double edgeW = nodes[seq-1][from]->getOutputEdge(to)->getWeight();
                double nodeW = nodes[seq-1][from]->getWeight();
                if (edgeW * nodeW > 0.0)
                    out << seq << ","
                        << frames->getFrames()->at(from) << ","
                        << frames->getFrames()->at(to) << ","
                        << nodeW << ","
                        << edgeW << ","
                        << edgeW * nodeW << "\n";
            }
    for (int from = 0; from < framesCount; from++) {
        double edgeW = 1.0;
        double nodeW = nodes[sequenceSize-1][from]->getWeight();
        if (edgeW * nodeW > 0.0)
            out << sequenceSize << ","
                << frames->getFrames()->at(from) << ","
                << "END" << ","
                << nodeW << ","
                << edgeW << ","
                << edgeW * nodeW << "\n";        
    }

    out.close();   
}
