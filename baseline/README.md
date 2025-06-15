## Baseline Implementation

- **Reference**: *Local Differentially Private Fuzzy Counting in Stream Data using Probabilistic Data Structures*.
- **Bloom Filter**: We adopt a standard Bloom Filter without modification, as the paper does not alter its original structure. The FPR is therefore governed by its classical theory.
- **Cuckoo Filter**: Our `insert()` method corresponds directly to Algorithm 1 in the paper.
- **Fuzzy Matching**: Our `query_count()` function implements Algorithm 3 in the paper, supporting segment-wise similarity estimation and threshold-based filtering.
- **Additions**: We additionally provide segment-level frequency counters and helper methods for evaluation convenience.
- We did not implement client–server separation, since our focus is the theoretical structure.
- **Autocorrection Support** : Although the original paper does not provide a complete autocorrection pipeline, we extend its fuzzy counting mechanism to support typo correction by maintaining a segment-to-word reverse map during insertion, counting segment hits to vote for most likely dictionary entries, wrapping this logic in `suggestion.py`, which provides both `suggest()` and `freq()` APIs.
