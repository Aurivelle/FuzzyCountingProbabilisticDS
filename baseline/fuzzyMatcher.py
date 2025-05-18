# Algorithm 3: Count querying with fuzzy matching (server-side)

from __future__ import annotations
from collections import Counter
from typing import Optional, List

from bloomFilter import BloomSegmenter
from cuckooFilter import CuckooFilter


class FuzzyMatcher:
    def __init__(
        self,
        st: float = 0.75,
        l: int = 128,
        k: int = 3,
        m: int = 4,
        q: int = 2,
        fp_len: Optional[int] = 16,
        bucket_ratio: int = 8,
    ):
        if not (0 < st <= 1):
            raise ValueError("st must be in (0, 1].")

        self.st = st
        self.segmenter = BloomSegmenter(l=l, k=k, m=m, q=q)
        self.cuckoo = CuckooFilter(
            num_buckets=bucket_ratio * m,
            bucket_size=4,
            fp_len=fp_len,
        )
        self._counts: Counter[str] = Counter()
        self._m = m
        

    def insert(self, text: str, weight: int = 1) -> None:
        for seg in self.segmenter.encode_and_segment(text):
            fp = seg.to01()
            self.cuckoo.insert(fp)
            self._counts[fp] += weight

    def query_similarity(self, text: str) -> float:
        segments = self.segmenter.encode_and_segment(text)
        hits = sum(self.cuckoo.query(seg.to01()) for seg in segments)
        return hits / self._m

    def is_match(self, text: str) -> bool:
        return self.query_similarity(text) >= self.st

    def query_count(self, text: str) -> int:
        segments = self.segmenter.encode_and_segment(text)
        hit_counts: List[int] = [
            self._counts.get(seg.to01(), 0) for seg in segments
        ]
        similarity = sum(c > 0 for c in hit_counts) / self._m
        if similarity < self.st:
            return 0
        nonzero = [c for c in hit_counts if c > 0]
        return min(nonzero) if nonzero else 0

    def stats(self) -> str:
        return (
            f"segments stored: {len(self.cuckoo):d} / {self.cuckoo.capacity} "
            f"({self.cuckoo.load_factor():.2%}), "
            f"unique fingerprints: {len(self._counts)}"
        )

    def __contains__(self, text: str) -> bool: 
        return self.is_match(text)


# Test part
if __name__ == "__main__":
    fm = FuzzyMatcher(st=0.5)

    for w in ["apple", "banana", "grape", "orange", "banana"]:
        fm.insert(w)

    for q in ["applle", "banana", "banan", "orenge", "grap", "pineapple"]:
        sim = fm.query_similarity(q)
        cnt = fm.query_count(q)
        print(f"{q:10s}  sim={sim:4.2f}  count≈{cnt:<2d}  match={fm.is_match(q)}")

    print(fm.stats())
