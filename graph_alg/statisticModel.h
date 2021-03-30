#pragma once

#include <math.h>

double log_neg_upper_bound(double x) {
    if (x == 0.0 )
        return std::numeric_limits<double>::infinity();
    else if (x == 1.0)
        return 0.0; // prevent -0.0, which causes problems with sanity conditions
    else
        return -log(x);
}

namespace StatisticModel {

    static double updateNodeWeight(const double weight, const double assignment) {
        return log_neg_upper_bound(assignment);
    }

    static double updateNodeWeight(const double weight, const double assignment, const double tfScore) {
        return log_neg_upper_bound(assignment * tfScore);
    }

    static double updateNodeWeight(const double weight, const double assignment, const double assignmentTOCSY, const double tfScore) {
        return log_neg_upper_bound(sqrt(assignment * assignmentTOCSY) * tfScore);
    }

    static double updateEdgeWeight(const double weight, const double edgeWeight, const double i1assignment) {
        return log_neg_upper_bound(sqrt(edgeWeight * i1assignment));
        //return edgeWeight;
    }

    static const double addNodeToWeight(const double weight, cNode* const node) {
        return weight + node->getWeight();
    }

    static const double addEdgeToWeight(const double weight, cEdge* const edge) {
        return weight + edge->getWeight();
    }

}
