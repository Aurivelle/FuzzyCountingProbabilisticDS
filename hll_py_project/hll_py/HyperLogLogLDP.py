import random
import math
from collections import defaultdict
from .HyperLogLog import HyperLogLog, SketchConfig
from .Hasher import str_to_u64


class HyperLogLogLDP:
    def __init__(self, cfg):
        self.cfg = cfg
        self.sketch_map = {}
        self.reported_item_hashes = set()

    def _random_or_true_hash(self, segment: str) -> int:
        p_true = math.exp(self.cfg.epsilon) / (math.exp(self.cfg.epsilon) + 1.0)
        if random.random() < p_true:
            return str_to_u64(segment)
        else:
            base = hash(segment)
            return base ^ random.getrandbits(64)

    def insert_segments(self, segments):
        for seg in segments:
            hash_val = self._random_or_true_hash(seg)
            if hash_val not in self.reported_item_hashes:
                self.reported_item_hashes.add(hash_val)
                if seg not in self.sketch_map:
                    self.sketch_map[seg] = HyperLogLog(self.cfg)
                self.sketch_map[seg].insert(hash_val)

    def estimate_word(self, word_key):
        matched = 0
        counts = []

        for i in range(self.cfg.m):
            seg = f"{word_key}_seg{i}"
            if seg in self.sketch_map:
                matched += 1
                counts.append(self.sketch_map[seg].estimate())

        if matched >= max(1, self.cfg.m // 2):
            return min(counts)
        return 0
