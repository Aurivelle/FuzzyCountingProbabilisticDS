// HyperLogLog.h by 吳竣凱 (B12201033)

// ======== INCLUDE ========= //
#pragma once
#include <vector>
#include <string>
#include <cstdint>
#include <unordered_map>
#include <unordered_set>

// ======== STRUCT ======== //
struct SketchConfig {
    int b = 4; // We use m = 2^b registers in HLL
    int m = 4; // Number of segments per word
    bool use_bias_correction = true;
    double alpha_override = -1.0; // Only use in place of alpha if > 0
    double epsilon = 4.0;
};

// ======== CLASSES ======== //
class HyperLogLog { // Pure HLL
public:
    // ~~~~~~~~~ FUNCTIONS ~~~~~~~~~~ //
    explicit HyperLogLog();
    explicit HyperLogLog(const SketchConfig& cfg);
    void insert(uint64_t hash);
    void insert(const std::string& str);
    double estimate() const;
    void merge(const HyperLogLog& other);
    void reset();
    std::string serialize() const;
    void deserialize(const std::string& data);
    uint8_t countZeroRegisters() const;
    uint8_t countNonzeroRegisters() const;
    uint8_t maxRegisterVal() const; // Max rho
    double estLocalSensitivity() const;
    size_t memoryUsage() const; // Memory used returned in bytes (Test metric?)
private:
    // ~~~~~~~~~ VARIABLES ~~~~~~~~~ //
    SketchConfig cfg;
    int m;
    double alpha_m;
    std::vector<uint8_t> registers;

    // ~~~~~~~~~ FUNCTIONS ~~~~~~~~~~ //
    double computeAlpha();
    uint8_t rho(uint64_t w_suffix) const; // Leading zeros + 1
};

class HyperLogLogLDP { // HLL used with LDP, uses HyperLogLog class
public:
    // ~~~~~~~~~ FUNCTIONS ~~~~~~~~~~ //
    explicit HyperLogLogLDP(const SketchConfig& cfg);
    void insertSegments(const std::vector<std::string>& segments);
    double estimateWord(const std::string& word_key);
private:
    // ~~~~~~~~~ VARIABLES ~~~~~~~~~ //
    SketchConfig cfg;
    std::unordered_map<std::string, HyperLogLog> sketch_map;
    std::unordered_set<uint64_t> reported_item_hashes;

    // ~~~~~~~~~ FUNCTIONS ~~~~~~~~~~ //
    uint64_t randomOrTrueHash(const std::string& segment) const;
};

// ======== HASHER ======== //
uint64_t murmur3_64(const std::string& key, uint64_t seed = 42);
uint64_t strToU64(const std::string& str);