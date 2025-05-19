// HyperLogLogAutocor.cpp by 吳竣凱 (B12201033)
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

    // Simulated segment insertions (as if from client with Bloom segments, with fake segments)
    // This part should be replaced with actual logic, this is definitely wrong, but it will require BloomCuckoo.cpp to code
    std::vector<std::string> words = {"apple", "banana", "grape", "orange", "banana"};
    for (const std::string& word : words) {
        std::vector<std::string> segments;
        for (int i = 0; i < cfg.m; ++i) {
            segments.push_back(word + "_seg" + std::to_string(i));
        }
        // Simulate fake/noisy segments
        segments.push_back("noise_A");
        segments.push_back("noise_B");
      
        std::cout << "[INSERT] " << word << " segments: ";
        for (const auto& seg : segments) std::cout << seg << " ";
        std::cout << std::endl;

        ldp.insertSegments(segments);
    }

    // Simulated segment-based queries (mimicking LDP-client segment naming)
    std::vector<std::string> queries = {"applle", "banana", "banana", "banana", "banan", "orenge", "grap", "pineapple"};

    std::cout << "\n[CHECK] Query Results:\n";
    for (const std::string& query : queries) {
        std::cout << "[QUERY] " << query << " segments: ";
        for (int i = 0; i < cfg.m; ++i) std::cout << query + "_seg" + std::to_string(i) << " ";
        std::cout << std::endl;

        int estimate = ldp.estimateWord(query);  // This will generate seg names like "applle_seg0"...
        std::cout << "  -> Estimated users: " << estimate << "\n-----------------------------\n";
    }

    return 0;
}