// HyperLogLogAutocor.cpp by 吳竣凱 (B12201033)
// Pure (non-LDP) fuzzy matching using q-gram HLL sketches

// ======== INCLUDE ======== //
#include "HyperLogLog.h"
#include <iostream>
#include <unordered_map>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>
#include <cstring>
#include <cstdint>

// ======== HELPER FUNCTION ======== //
// Extract fixed-length q-grams from a word (e.g., "definitely" -> "def", "efi", ...)
std::vector<std::string> extractQgrams(const std::string& word, int q = 2) {
    std::vector<std::string> grams;
    if (word.size() < q) return grams;
    for (size_t i = 0; i <= word.size() - q; ++i) {
        grams.push_back(word.substr(i, q));
    }
    return grams;
}

// ======== MAIN ======== //
int main() {
    SketchConfig cfg;
    cfg.b = 4; // 16 registers per HLL

    std::unordered_map<std::string, HyperLogLog> qgram_sketches;

    // Simulated user inputs with typos or variations
    std::vector<std::pair<std::string, std::string>> user_inputs = {
        {"u1", "apple"},
        {"u2", "banana"},
        {"u3", "grape"},
        {"u4", "orange"},
        {"u5", "banana"}
    };

    // Insert user word q-grams into their respective sketches
    for (const auto& [user, word] : user_inputs) {
        // std::cout << "[DEBUG] Inserting word: " << word << " from user: " << user << "\n";
        auto qgrams = extractQgrams(word, 2);
        for (const auto& q : qgrams) {
            if (!qgram_sketches.count(q)) {
                qgram_sketches.emplace(q, cfg);
            }
            // std::cout << "[DEBUG] inserting into qgram '" << q << "' with hash " << murmur3_64(q) << "\n";
            qgram_sketches[q].insert(q + "_" + user);
        }
    }

    // Queries for fuzzy matches
    std::vector<std::string> queries = {"applle", "banana", "banan", "orenge", "grap", "pineapple"};
    std::cout << "\n[CHECK] Raw estimates for all q-grams:\n";
    for (const auto& [q, sketch] : qgram_sketches) {
        std::cout << "  -> " << q << ": " << sketch.estimate() << "\n";
    }

    for (const auto& query : queries) {
        auto qgrams = extractQgrams(query, 2);
        std::vector<int> estimates;

        std::cout << std::setw(10) << query << " -> matched segments: ";
        for (const auto& q : qgrams) {
            if (qgram_sketches.count(q)) {
                int est = qgram_sketches[q].estimate();
                estimates.push_back(est);
                std::cout << q << "(" << est << ") ";
            }
        }
        std::cout << "\n";

        if (estimates.size() >= 3) {
            int result = *std::min_element(estimates.begin(), estimates.end());
            std::cout << "  -> Estimated users for '" << query << "': " << result << "\n";
        } else {
            std::cout << "  -> Not enough matching segments to estimate\n";
        }
        std::cout << "-----------------------------\n";
    }

    return 0;
}