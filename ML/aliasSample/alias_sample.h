#pragma once

#include <torch/extension.h>
#include <map>
#include <string>
#include <stack>

/*
 * A probability distribution for discrete weighted random variables and its probability/alias
 *  tables for efficient sampling via Vose's Alias Method (a good explanation of which can be found at
 *  http://www.keithschwarz.com/darts-dice-coins/).
 */
class AliasSample {
public:
    AliasSample(const torch::Tensor& dist) {
        Init(dist);
    }

    void Init(const torch::Tensor& dist);

    int64_t Sample() const;

    int64_t operator()() const {
        return Sample();
    }

    std::string Str() const;

private:
    torch::Tensor prob;   // float
    torch::Tensor alias;  // long
};


// Construct probability and alias tables for the distribution
void AliasSample::Init(const torch::Tensor& dist) {
    auto n = dist.size(0);
    // probability list
    prob = torch::zeros(n, dist.options().dtype(torch::kFloat));
    // alias list
    alias = torch::zeros(n, dist.options().dtype(torch::kLong));

    std::stack<int64_t> smaller, larger;
    auto dist_d = dist.to(torch::kFloat).data<float>();
    auto prob_d = prob.data<float>();
    auto alias_d = alias.data<int64_t>();
    // Construct and sort the scaled probabilities into their appropriate stacks
    for (ptrdiff_t i = 0; i < n; ++i) {
        prob_d[i] = dist_d[i] * n;
        if (prob_d[i] < 1.0) {
            smaller.push(i);
        } else {
            larger.push(i);
        }
    }
    // Construct the probability and alias tables
    int64_t small, large;
    while (!smaller.empty() && !larger.empty()) {
        small = smaller.top();
        smaller.pop();
        large = larger.top();
        larger.pop();
        alias_d[small] = large;
        prob_d[large] = prob_d[large] + prob_d[small] - 1.0;
        if (prob_d[large] < 1.0) {
            smaller.push(large);
        } else {
            larger.push(large);
        }
    }
}  // Init

int64_t AliasSample::Sample() const {
    auto col = torch::randint(prob.size(0), 1, alias.options()).data<int64_t>()[0];
    auto rd = torch::rand(1, prob.options()).data<float>()[0];
    return rd < prob.data<float>()[col] ? col : alias.data<int64_t>()[col];
}

std::string AliasSample::Str() const {
    auto n = prob.size(0);
    auto prob_d = prob.data<float>();
    auto alias_d = alias.data<int64_t>();
    std::string result = "prob: {";
    for (ptrdiff_t i = 0; i < n; ++i) {
        result += std::to_string(prob_d[i]);
        result += ", ";
    }
    result += "}\n";
    result += "alias: {";
    for (ptrdiff_t i = 0; i < n; ++i) {
        result += std::to_string(alias_d[i]);
        result += ", ";
    }
    result += "}\n";
    return result;
}
