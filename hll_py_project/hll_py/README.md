# How to use this library

```
# pip install package
pip install hll_py

# import hll_py
from hll_py import autocorrect

# main
history_input = [("u1","apple"),
    ("u2", "banana"),
    ("u3", "grape"),
    ("u4", "orange"),
    ("u5", "banana")
]
queries = ["applle", "banana", "banan", "orenge", "grap", "pineapple"]

results = autocorrect(history_input, queries)
