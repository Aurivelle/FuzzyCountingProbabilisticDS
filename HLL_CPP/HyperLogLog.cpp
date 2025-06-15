// HyperLogLog.cpp by 吳竣凱 (B12201033)
// Implements the HyperLogLog class for cardinality estimation.

// ======== INCLUDE ========= //
#include "HyperLogLog.h"
#include <bit>
#include <bitset>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <sstream>
#include <iostream>

// ========= FALLBACK ======== //
uint8_t clz(uint64_t num) {
    if (num == 0) {
        return 64;
    }
#if __cplusplus >= 202002L && defined(__cpp_lib_bit_ops) && __cpp_lib_bit_ops >= 201907L
    // C++20 and <bit> header with bit operations are available
    return (uint8_t)(std::countl_zero(num));
#elif defined(__GNUC__) || defined(__clang__)
    // Fallback to GCC/Clang intrinsic
    return (uint8_t)(__builtin_clzll(num));
#else
    // Basic fallback (less efficient)
    uint8_t count = 0;
    uint64_t mask = 1ULL << 63;
    while (mask > 0 && (num & mask) == 0) {
        ++count;
        mask >>= 1;
    }
    return count;
#endif
}

// ======== HyperLogLog CLASS IMPLEMENTATION ======== //
HyperLogLog::HyperLogLog() : HyperLogLog(SketchConfig()) {}

HyperLogLog::HyperLogLog(const SketchConfig& cfg) : cfg(cfg) {
    if (cfg.b > 16) { // Practical bounds
        throw std::invalid_argument("Precision b must be less than 16.");
    }
    this->m = 1 << cfg.b;
    this->registers.assign(this->m, 0);
    this->alpha_m = (cfg.alpha_override > 0) ? cfg.alpha_override : this->computeAlpha();
}

// ======== PRIVATE ======== //
double HyperLogLog::computeAlpha() {
    if (cfg.alpha_override > 0) {
        alpha_m = cfg.alpha_override;
        return alpha_m;
    }

    // These are values from the original 2007 paper
    if (m == 16) { alpha_m = 0.673; return alpha_m; }
    if (m == 32) { alpha_m = 0.697; return alpha_m; }
    if (m == 64) { alpha_m = 0.709; return alpha_m; }
    if (m == 0) throw std::logic_error("m cannot be 0.");

    alpha_m = 0.7213 / (1.0 + 1.079 / (double)(m));
    return alpha_m;
}

uint8_t HyperLogLog::rho(uint64_t w_suffix) const {
    // w_suffix has (64 - b) LSB
    int w_bits = 64 - cfg.b;
    if (w_bits <= 0) return 1;

    if (w_suffix == 0) {
        return (uint8_t)(w_bits + 1);
    }

    // Shift left to align the relevant bits to the MSB
    uint64_t shifted = w_suffix << cfg.b;
    int leading_zeros = clz(shifted);

    return static_cast<uint8_t>(leading_zeros + 1);
}

// ======= PUBLIC ======= //
void HyperLogLog::insert(uint64_t hash) {
    // Determine register index (j)
    int register_idx = (int)(hash >> (64 - cfg.b));

    // Determine w (The remaining 64 - b bits)
    uint64_t w_mask = (1ULL << (64 - cfg.b)) - 1;
    uint64_t w_suffix = hash & w_mask;

    uint8_t rho_w = rho(w_suffix);
    
    if (rho_w > registers[register_idx]) {
        registers[register_idx] = rho_w;
    }

    // std::cout << "Inserted hash into register " << register_idx << " with rho = " << (int)rho_w << "\n";
    // std::cout << "Non-zero registers: " << countNonzeroRegisters() << "\n";
}

void HyperLogLog::insert(const std::string& str) {
    insert(strToU64(str));
}

double HyperLogLog::estimate() const {
    // Normal implementation
    double sum_inv_powers = 0.0;
    for (uint8_t reg_val : registers) {
        sum_inv_powers += std::pow(2.0, -(double)(reg_val));
    }

    double estimate_val = alpha_m * m * m / sum_inv_powers;
    // std::cout << "Raw estimate: " << estimate_val << ", Z = " << sum_inv_powers << std::endl;

    // Small range correction
    if (cfg.use_bias_correction && estimate_val <= 2.5 * m) {
        uint8_t zero_reg_count = countZeroRegisters(); // "V" in the paper    
        if (zero_reg_count > 0) {
            estimate_val = m * std::log(static_cast<double>(m) / zero_reg_count);
        }
    }

    // Large range correction
    else if (cfg.use_bias_correction && estimate_val > (1.0 / 30.0) * std::pow(2.0, 32)) {
        estimate_val = -std::pow(2.0, 32) * std::log(1.0 - estimate_val / std::pow(2.0, 32));
    }

    return estimate_val;
}

void HyperLogLog::merge(const HyperLogLog& other) {
    if (this->m != other.m || this->cfg.b != other.cfg.b) {
        throw std::invalid_argument("Cannot merge HLL with different precision");
    }

    // Merge by taking max
    for (int i = 0; i < m; ++i) {
        if (other.registers[i] > this->registers[i]) {
            this->registers[i] = other.registers[i];
        }
    }
}

void HyperLogLog::reset() {
    std::fill(registers.begin(), registers.end(), 0);
}

// Privacy related function
std::string HyperLogLog::serialize() const {
    // This is a simple serialization, a more robust version could be used instead
    std::ostringstream oss;
    oss.put((char)(cfg.b));
    for (auto reg : registers) {
        oss.put((char)(reg));
    }
    return oss.str();
}

// Privacy related function
void HyperLogLog::deserialize(const std::string& data) {
    if (data.empty()) {
        throw std::invalid_argument("Cannot deserialize from empty string.");
    }

    int deserialized_b = (int)((unsigned char)(data[0]));

    if (deserialized_b < 4 || deserialized_b > 16) { // Validate b
        throw std::runtime_error("Deserialized b value is out of valid range (4-16).");
    }
    this->cfg.b = deserialized_b;
    this->m = 1 << this->cfg.b;

    // Expected size: 1 byte for 'b' + m bytes for registers
    if (data.size() != 1 + (size_t)(this->m)) {
        throw std::runtime_error("Deserialization data size mismatch for the given b.");
    }

    this->registers.resize(this->m);
    for (int i = 0; i < this->m; ++i) {
        this->registers[i] = (uint8_t)((unsigned char)(data[i + 1]));
    }
    // Re-calculate alpha_m based on the new m (derived from deserialized b)
    this->alpha_m = (cfg.alpha_override > 0) ? cfg.alpha_override : this->computeAlpha();
}

uint8_t HyperLogLog::countZeroRegisters() const {
    return std::count_if(registers.begin(), registers.end(), [](uint8_t r) { return r == 0; });
}

uint8_t HyperLogLog::countNonzeroRegisters() const {
    return std::count_if(registers.begin(), registers.end(), [](uint8_t r) { return r > 0; });
}

uint8_t HyperLogLog::maxRegisterVal() const{ // Max rho
    if (registers.empty()) return 0;
    return *std::max_element(registers.begin(), registers.end());
}

double HyperLogLog::estLocalSensitivity() const {
    int nonzero = countNonzeroRegisters();
    return (nonzero == 0) ? 1.0 : 1.0 / (double)(nonzero);
}

size_t HyperLogLog::memoryUsage() const {
    return sizeof(cfg) + sizeof(m) + (registers.capacity() * sizeof(uint8_t)) + sizeof(alpha_m);
}