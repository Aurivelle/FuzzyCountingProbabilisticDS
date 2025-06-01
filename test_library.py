from hll_py import AutoCorrector

# main
history_input = [("u1","apple"),
    ("u2", "banana"),
    ("u3", "grape"),
    ("u4", "orange"),
    ("u5", "banana")
]
queries = ["applle", "banana", "banan", "orenge", "grap", "pineapple"]

results = AutoCorrector.autocorrect(history_input, queries)