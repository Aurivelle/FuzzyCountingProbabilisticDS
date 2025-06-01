from HyperLogLog import SketchConfig, HyperLogLog
from collections import defaultdict

def extract_qgrams(word, q=2):
    if len(word) < q:
        return []
    return [word[i:i+q] for i in range(len(word) - q + 1)]

def load_words(filename):
    with open(filename, 'r') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def autocorrect(user_inputs, queries, q=2, b=4, output_file="suggestions.txt"):
    cfg = SketchConfig(b=b)
    qgram_sketches = {}
    qgram_to_words = defaultdict(set)
    suggestions = []

    for idx, word in enumerate(user_inputs):
        user = f"u{idx+1}"
        qgrams = extract_qgrams(word, q)
        for gram in qgrams:
            qgram_to_words[gram].add(word)
            if gram not in qgram_sketches:
                qgram_sketches[gram] = HyperLogLog(cfg)
            qgram_sketches[gram].insert(f"{gram}_{user}")

    print("\n[CHECK] Raw estimates for all q-grams:")
    for gram, sketch in qgram_sketches.items():
        print(f"  -> {gram}: {sketch.estimate()}")

    for query in queries:
        qgrams = extract_qgrams(query, q)
        candidate_scores = defaultdict(int)

        print(f"{query:>10} -> matched segments: ", end="")
        best_match = ""
        best_score = 0

        matched_qgrams = []
        merged_sketch = HyperLogLog(cfg)

        for gram in qgrams:
            if gram in qgram_sketches:
                est = qgram_sketches[gram].estimate()
                print(f"{gram}({est}) ", end="")
                matched_qgrams.append(gram)
                merged_sketch.merge(qgram_sketches[gram])
                for candidate in qgram_to_words[gram]:
                    candidate_scores[candidate] += est
                    if candidate_scores[candidate] > best_score:
                        best_score = candidate_scores[candidate]
                        best_match = candidate
        print()

        if len(matched_qgrams) >= 3:
            print(f"  -> Estimated users: {merged_sketch.estimate():}")
            if best_match:
                print(f"  -> Suggested correction: {best_match}")
                suggestions.append(best_match)
        else:
            print("  -> Not enough matching segments to estimate")
            suggestions.append("")
        print("-" * 30)

    # Write all best matches to output file
    with open(output_file, "w") as out:
        out.write("\n".join(suggestions))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <inputs_file> <queries_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    query_file = sys.argv[2]

    user_inputs = load_words(input_file)
    queries = load_words(query_file)
    autocorrect(user_inputs, queries, q=2, b=4, output_file="suggestions.txt")

