# I wrote this description before 吳述宇 pushed his code and I realized it was in Python

# HyperLogLog Code Description (Section By 吳竣凱)
I plan to write my code so that it can be implemented in this structure:

```
/src/
  └─ /hll/
      ├─ HyperLogLog.h               // Shared header for both variants
      ├─ Hasher.cpp                  // Implements the Murmur3_64 hash
      ├─ HyperLogLog.cpp             // Pure HLL sketch (not LDP-specific)
      ├─ HyperLogLogAutocor.cpp      // Pure HLL Autocorrection
      ├─ HyperLogLogLDP.cpp          // HLL with LDP logic, integrates into Bloom
      └─ HyperLogLogLDPAutocor.cpp   // HLL Autocorrection with LDP logic simulation
  └─ /baseline/
      └─ BloomCuckoo.cpp             // Original fingerprint-based system
  └─ /test/                          // Test and benchmark files
      ├─ BloomCuckooTest.cpp         // Tests for the baseline
      ├─ PureHLLTest.cpp             // Tests for the standalone HLL sketch
      └─ HLLBloomCuckoo.cpp          // Tests for the integrated HLL-LDP version
main.cpp                             // Whatever library wrapper
```

My section will only write the files under `/hll/`

## Integration Notes

To switch from the Bloom+Cuckoo fingerprint design to HLL with LDP:

- Replace the original `std::vector<uint64_t> bucket` (or equivalent) with a `HyperLogLog` sketch per bucket.
- Most of the fingerprint logic can remain, but now sketch-based estimation replaces exact fingerprint counting.

In `HyperLogLogLDP.cpp`, I simulate storing HyperLogLog sketches in place of fingerprints in the original algorithm.

# Notes on `HyperLogLogLDPAutocor.cpp`
Since I didn’t yet have access to the full BloomCuckoo implementation when building the LDP autocorrection, I used a standalone simulation based on:
 - Injecting real and fake segments
 - Estimating via segment overlap
 - Testing noise robustness

This shows the core functionality required for LDP-based buckets:
 - [OK] Noise tolerance
 - [OK] Segment-level estimation
 - [OK] Drop-in compatibility with the BloomCuckoo structure

# Basic Structure of HyperLogLog.h
```
struct SketchConfig
class HyperLogLog
class HyperLogLogLDP
```

# Compilation
To test the standalone pure HLL:

```
g++ HyperLogLogAutocor.cpp HyperLogLog.cpp HyperLogLogLDP.cpp Hasher.cpp -std=c++20
./a.out
```

To test the LDP sketch simulation:

```
g++ HyperLogLogLDPAutocor.cpp HyperLogLog.cpp HyperLogLogLDP.cpp Hasher.cpp -std=c++20
./a.out
```

# Remark
Here for testing purposes, I set `cfg.b = 4`. For larger data sets, I suggest using `10 ≤ cfg.b ≤ 16`

# References
 - Original paper on LDP, i.e. [Locally Differentially Private Fuzzy Conting in Stream Data using Probabilistic Data Strctures [VBA22]](https://ieeexplore.ieee.org/document/9855874) (`/ref/ldp_bloom_cuckoo.pdf`)
 - [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm [Fla+07]](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) (`/ref/hyperloglog.pdf`) to implement HyperLogLog