# Algorithm 1: Insertion (Server-side)
from __future__ import annotations
import random
from typing import List, Optional

import mmh3


class CuckooFilter:
    def __init__(
        self,
        num_buckets: int = 64,
        bucket_size: int = 4,
        max_kicks: int = 500,
        fp_len: Optional[int] = 16,
    ):
        self.num_buckets = num_buckets
        self.init_bucket_size = bucket_size
        self.max_kicks = max_kicks
        self.fp_len = fp_len
        self._buckets: List[List[str]] = [[] for _ in range(num_buckets)]
        self._limits: List[int] = [bucket_size] * num_buckets

    def _i1(self, fp: str) -> int:
        return mmh3.hash(fp, 17, signed=False) % self.num_buckets

    def _i2(self, i1: int, fp: str) -> int:
        return (i1 ^ mmh3.hash(fp, 31, signed=False)) % self.num_buckets

    def _is_full(self, idx: int) -> bool:
        return len(self._buckets[idx]) >= self._limits[idx]
    
    def insert(self, raw_fp: str) -> bool:
        fp = raw_fp
        i1 = self._i1(fp)
        i2 = self._i2(i1, fp)

        # --- Either bucket has space ---------------------------
        for idx in (i1, i2):
            if not self._is_full(idx):
                self._buckets[idx].append(fp)
                return True
            
        idx = random.choice((i1, i2))
        for _ in range(self.max_kicks):
            if not self._buckets[idx]:  
                break
            victim_pos = random.randrange(len(self._buckets[idx]))
            fp, self._buckets[idx][victim_pos] = (
                self._buckets[idx][victim_pos],
                fp,
            )
            idx = self._i2(idx, fp)
            if not self._is_full(idx):
                self._buckets[idx].append(fp)
                return True

        # --- Adaptive expansion  -------------------------
        self._limits[i1] *= 2  
        self._buckets[i1].append(fp)
        return True

    def query(self, raw_fp: str) -> bool:
        fp = raw_fp
        i1 = self._i1(fp)
        i2 = self._i2(i1, fp)
        return fp in self._buckets[i1] or fp in self._buckets[i2]

    def __len__(self) -> int:
        return sum(len(b) for b in self._buckets)

    @property
    def capacity(self) -> int:
        return sum(self._limits)
    def load_factor(self) -> float:
        return len(self) / self.capacity if self.capacity else 0.0
    def bucket_lengths(self) -> List[int]:
        return [len(b) for b in self._buckets]


# Test Part
if __name__ == "__main__":
    from bloomFilter import BloomSegmenter

    seg = BloomSegmenter(l=128, k=3, m=4, q=2)
    cf = CuckooFilter(num_buckets=8, bucket_size=2, fp_len=16)

    words = ["apple", "banana", "orange", "grape", "mango", "melon", "berry"]
    for w in words:
        for s in seg.encode_and_segment(w):
            cf.insert(s.to01())

    print("Bucket lengths:", cf.bucket_lengths())
    print("Capacity:", cf.capacity, "Stored:", len(cf), "Load:", f"{cf.load_factor():.2%}")
