# How to use this library

```
from hll_py import HyperLogLog, HyperLogLogLDP, autocorrect

cfg = HyperLogLog.SketchConfig(b=4)
hll = HyperLogLog.HyperLogLog(cfg)

# Use hll
results = autocorrect(user_inputs, queries)

```
