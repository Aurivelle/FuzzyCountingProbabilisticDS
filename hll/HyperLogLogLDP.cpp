// HyperLogLogLDP.cpp by 吳竣凱 (B12201033)
// Implements the HyperLogLogLDP class for a replacement of the buckets in Bloom + Cuckoo.

// ======== INCLUDE ========= //
#include "HyperLogLog.h"
#include <random>     // For LDP randomization
#include <cmath>      
#include <iostream> 

// ======== HyperLogLogLDP CLASS IMPLEMENTATION ======== //
HyperLogLogLDP::HyperLogLogLDP(const SketchConfig& cfg) : cfg(cfg) {}

// ======== PRIVATE ======== //
uint64_t HyperLogLogLDP::randomOrTrueHash(const std::string& segment) const {
    double p_true = std::exp(cfg.epsilon) / (std::exp(cfg.epsilon) + 1.0);

    // Use a static RNG seeded once per program run
    static std::random_device rd;
    static std::mt19937_64 rng(rd());
    std::uniform_real_distribution<double> dist(0.0, 1.0);

    if (dist(rng) < p_true) {
        return strToU64(segment);
    } else {
        // Make randomized hash dependent on the segment too
        std::hash<std::string> hasher;
        size_t base = hasher(segment);
        std::uniform_int_distribution<uint64_t> random_hash_dist(0, UINT64_MAX);

        return base ^ random_hash_dist(rng); // XOR deterministic base with noise
    }
}

// ======== PUBLIC ======== //
void HyperLogLogLDP::insertSegments(const std::vector<std::string>& segments) {
    static std::random_device rd;
    static std::mt19937_64 rng(rd());

    for (const auto& seg : segments) {
        uint64_t hash = randomOrTrueHash(seg);
        if (!reported_item_hashes.count(hash)) {
            reported_item_hashes.insert(hash);
            if (!sketch_map.count(seg)) {
                sketch_map.emplace(seg, cfg); // Supply cfg at creation
            }
            sketch_map[seg].insert(hash);
        }
    }
}

double HyperLogLogLDP::estimateWord(const std::string& word_key) {
    int matched = 0;
    
    std::vector<int> counts;

    for (int i = 0; i < cfg.m; ++i) {
        std::string seg = word_key + "_seg" + std::to_string(i);
        // std::cout << "  [CHECK] Looking for segment: " << seg;
        if (sketch_map.count(seg)) {
            // std::cout << " -> FOUND, est=" << sketch_map[seg].estimate() << "\n";
            matched++;
            counts.push_back(sketch_map[seg].estimate());
        } else {
            // std::cout << " -> NOT FOUND\n";
        }
    }

    if (matched >= std::max(1, cfg.m / 2)) { // Threshold: majority match
        return *std::min_element(counts.begin(), counts.end());
    }

    return 0;
}