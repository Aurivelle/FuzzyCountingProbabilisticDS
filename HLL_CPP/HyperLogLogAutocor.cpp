// HyperLogLogAutocor_Candidates.cpp — Pure HLL autocorrection with segment-to-word mapping
#include "HyperLogLog.h"
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>
#include <cstdint>

// Extract fixed-length q-grams
std::vector<std::string> extractQgrams(const std::string& word, int q = 2) {
    std::vector<std::string> grams;
    if (word.size() < q) return grams;
    for (size_t i = 0; i <= word.size() - q; ++i) {
        grams.push_back(word.substr(i, q));
    }
    return grams;
}

int main() {
    SketchConfig cfg;
    cfg.b = 4; // 16 registers per HLL

    std::unordered_map<std::string, HyperLogLog> qgram_sketches;
    std::unordered_map<std::string, std::unordered_set<std::string>> qgram_to_words;
    std::unordered_set<std::string> dictionary;

    std::vector<std::pair<std::string, std::string>> user_inputs = {
        {"u1", "apple"},
        {"u2", "banana"},
        {"u3", "grape"},
        {"u4", "orange"},
        {"u5", "banana"}
    };

    for (const auto& [user, word] : user_inputs) {
        dictionary.insert(word);
        auto qgrams = extractQgrams(word);
        for (const auto& q : qgrams) {
            qgram_to_words[q].insert(word);
            if (!qgram_sketches.count(q)) {
                qgram_sketches[q] = HyperLogLog(cfg);
            }
            qgram_sketches[q].insert(q + "_" + user);
        }
    }

    std::vector<std::string> queries = {"applle", "banana", "banan", "orenge", "grap", "pineapple"};

    std::cout << "\n[CHECK] Raw estimates for all q-grams:\n";
    for (const auto& [q, sketch] : qgram_sketches) {
        std::cout << "  -> " << q << ": " << sketch.estimate() << "\n";
    }

    for (const auto& query : queries) {
        auto qgrams = extractQgrams(query);
        std::unordered_map<std::string, int> candidate_scores;
        std::vector<double> matched_estimates;

        std::cout << std::setw(10) << query << " -> matched segments: ";

        std::string best_match;
        int best_score = 0;

        for (const auto& q : qgrams) {
            if (qgram_sketches.count(q)) {
                double est = qgram_sketches[q].estimate();
                matched_estimates.push_back(est);
                std::cout << q << "(" << est << ") ";

                for (const auto& candidate : qgram_to_words[q]) {
                    candidate_scores[candidate]++;
                    if (candidate_scores[candidate] > best_score) {
                        best_score = candidate_scores[candidate];
                        best_match = candidate;
                    }
                }
            }
        }
        std::cout << "\n";

        if (matched_estimates.size() >= 3) {
            double min_est = *std::min_element(matched_estimates.begin(), matched_estimates.end());
            std::cout << "  -> Estimated users: " << min_est << "\n";

            if (!best_match.empty()) {
                std::cout << "  -> Suggested correction: " << best_match << "\n";
            }
        } else {
            std::cout << "  -> Not enough matching segments to estimate\n";
        }
        std::cout << "-----------------------------\n";
    }

    return 0;
}
