import math
from typing import List
from .Hasher import str_to_u64

class SketchConfig:
    def __init__(self, b=4, m=4, use_bias_correction=True, alpha_override=-1.0, epsilon=4.0):
        self.b = b
        self.m = m
        self.use_bias_correction = use_bias_correction
        self.alpha_override = alpha_override
        self.epsilon = epsilon

class HyperLogLog:
    def __init__(self, cfg=SketchConfig()):
        self.cfg = cfg
        self.m = 2 ** self.cfg.b
        self.alpha_m = self.compute_alpha()
        self.registers = [0] * self.m

    def compute_alpha(self):
        if self.cfg.alpha_override > 0:
            return self.cfg.alpha_override
        if self.m == 16:
            return 0.673
        elif self.m == 32:
            return 0.697
        elif self.m == 64:
            return 0.709
        else:
            return 0.7213 / (1 + 1.079 / self.m)

    def rho(self, w_suffix):
        if w_suffix == 0:
            return 64
        return (w_suffix.bit_length() - 1) ^ 63
        # return (w_suffix.bit_length() - w_suffix.bit_length() + 1
        #         if w_suffix == 0 else
        #         64 - w_suffix.bit_length() + 1)

    def insert(self, value):
        if isinstance(value, str):
            hash_val = str_to_u64(value)
        else:
            hash_val = value
        j = hash_val >> (64 - self.cfg.b)
        w = hash_val << self.cfg.b
        self.registers[j] = max(self.registers[j], self.rho(w))

    def merge(self, other):
        if self.m != other.m:
            raise ValueError("Cannot merge HLLs with different number of registers")
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])

    def estimate(self):
        Z = sum([2 ** -r for r in self.registers])
        E = self.alpha_m * self.m ** 2 / Z
        V = self.registers.count(0)
        if E <= 5/2 * self.m:
            return self.m * math.log(self.m / V) if V != 0 else E
        elif E <= 1/30 * (1 << 64):
            return E
        else:
            return - (1 << 64) * math.log(1 - E / (1 << 64))

    def reset(self):
        self.registers = [0] * self.m
