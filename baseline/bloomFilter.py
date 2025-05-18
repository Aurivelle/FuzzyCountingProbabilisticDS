# Traditional Implementation of Bloom Filter

from __future__ import annotations

import math
from typing import List, Sequence

import mmh3
from bitarray import bitarray


class BloomSegmenter:

    def __init__(self, l: int = 128, k: int = 3, m: int = 4, q: int = 2) -> None:
        self.l, self.k, self.m, self.q = l, k, m, q
        self._seg_len = l // m

    def encode(self, text: str) -> bitarray:
        bf = bitarray(self.l)
        bf.setall(0)

        for token in self._qgrams(text):
            for seed in range(self.k):
                idx = mmh3.hash(token, seed, signed=False) % self.l
                bf[idx] = 1
        return bf

    def segment(self, bf: bitarray) -> List[bitarray]:
        if len(bf) != self.l:
            raise ValueError("bitarray length mismatch.")
        return [bf[i * self._seg_len : (i + 1) * self._seg_len] for i in range(self.m)]

    def encode_and_segment(self, text: str) -> List[bitarray]:
        return self.segment(self.encode(text))


    def fp_rate(self, n_items: int) -> float:

        return (1 - math.exp(-self.k * n_items / self.l)) ** self.k

    def _qgrams(self, text: str) -> Sequence[str]:
        if self.q == 1 or len(text) <= self.q:
            return (text,)
        return (text[i : i + self.q] for i in range(len(text) - self.q + 1))


# Test Part
if __name__ == "__main__":
    seg = BloomSegmenter(l=128, k=3, m=4, q=2)
    bitvec = seg.encode("apple")
    segments = seg.segment(bitvec)

    print(f"Full Bloom Vector ({len(bitvec)} bits):\n{bitvec.to01()}")
    print("-" * 60)
    for i, s in enumerate(segments):
        print(f"Segment {i} ({s.count()} ones): {s.to01()}")
