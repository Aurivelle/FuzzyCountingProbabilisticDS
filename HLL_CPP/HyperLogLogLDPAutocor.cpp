// HyperLogLogLDPAutocor.cpp by 吳竣凱 (B12201033)
// This is only a demonstration of the HyperLogLog's ability to deal with noise, it cannot be used unless combined with BloomCuckoo.cpp
// ======== INCLUDE ======== //
#include "HyperLogLog.h"
#include <iostream>
#include <vector>
#include <string>

// ======== MAIN ======== //
int main() {
    SketchConfig cfg;
    cfg.b = 4;
    cfg.epsilon = 4.0;
    cfg.m = 4;
    HyperLogLogLDP ldp(cfg);

    std::unordered_map<std::string, std::unordered_set<std::string>> segment_to_words;
    std::unordered_set<std::string> dictionary;

    // Simulated segment insertions (as if from client with Bloom segments, with fake segments)
    std::vector<std::string> words = {"apple", "banana", "grape", "orange", "banana"};
    for (const std::string& word : words) {
        dictionary.insert(word);
        std::vector<std::string> segments;
        for (int i = 0; i < cfg.m; ++i) {
            std::string seg = word + "_seg" + std::to_string(i);
            segments.push_back(seg);
            segment_to_words[seg].insert(word);
        }
        // Simulate fake/noisy segments
        segments.push_back("noise_A");
        segments.push_back("noise_B");
        for (int i = 0; i < cfg.m; ++i) {
            segments.push_back(word + "_seg" + std::to_string(i));
        }
        std::cout << "[INSERT] " << word << " segments: ";
        for (const auto& seg : segments) std::cout << seg << " ";
        std::cout << std::endl;
      
        ldp.insertSegments(segments);
    }

    // Simulated segment-based queries (mimicking LDP-client segment naming)
    std::vector<std::string> queries = {"applle", "banana", "banan", "orenge", "grap", "pineapple"};

    std::cout << "\n[CHECK] Query Results:\n";
    for (const std::string& query : queries) {
        std::cout << "[QUERY] " << query << " segments: ";
        for (int i = 0; i < cfg.m; ++i) std::cout << query + "_seg" + std::to_string(i) << " ";
        std::cout << std::endl;
      
        // Segment-to-word matching
        std::string best_match;
        int best_score = 0;
        std::unordered_map<std::string, int> candidate_scores;
        
        for (int i = 0; i < cfg.m; ++i) {
            std::string seg = query + "_seg" + std::to_string(i);
            if (segment_to_words.count(seg)) {
                for (const auto& candidate : segment_to_words[seg]) {
                    candidate_scores[candidate]++;
                    if (candidate_scores[candidate] > best_score) {
                        best_score = candidate_scores[candidate];
                        best_match = candidate;
                    }
                }
            }
        }
        
        int estimate = ldp.estimateWord(query);
        std::cout << "  -> Estimated users: " << estimate << "\n";
        if (!best_match.empty()) std::cout << "  -> Suggested correction: " << best_match << "\n";
        std::cout << "-----------------------------\n";
    }

    return 0;
}
