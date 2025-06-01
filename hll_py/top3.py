from collections import defaultdict, Counter
from HyperLogLog import HyperLogLog, SketchConfig
from pathlib import Path

def extract_qgrams(word, q=2):
    return [word[i:i+q] for i in range(len(word) - q + 1)] if len(word) >= q else []

def load_vocab_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

class Top3HLLSuggester:
    def __init__(self, vocab, b=4, q=2):
        if isinstance(vocab, (str, Path)):
            vocab = load_vocab_from_file(vocab)

        self.q = q
        self.cfg = SketchConfig(b=b)
        self.qgram_to_words = defaultdict(set)
        self.qgram_sketches = {}
        total = len(vocab)

        for idx, word in enumerate(vocab):
            user = f"user{idx+1}" # Fake user ID per word
            if idx % 10000 == 0 and idx > 0:
                print(f"[INFO] 已處理 {idx}/{total} 個詞")

            for gram in extract_qgrams(word, q):
                self.qgram_to_words[gram].add(word)
                if gram not in self.qgram_sketches:
                    self.qgram_sketches[gram] = HyperLogLog(self.cfg)
                self.qgram_sketches[gram].insert(f"{gram}_{user}") # Simulate user input

        self.vocab = set(vocab)

    def suggest(self, query, top_k=3, min_votes=1):
        qgrams = extract_qgrams(query, self.q)
        vote_counter = Counter()
        popularity = defaultdict(float)

        for gram in qgrams:
            if gram not in self.qgram_to_words:
                continue
            est = self.qgram_sketches[gram].estimate()
            for word in self.qgram_to_words[gram]:
                vote_counter[word] += 1
                popularity[word] += est  # accumulate user estimates

        if not vote_counter:
            return []

        scored = [
            (word, (votes, popularity[word]))
            for word, votes in vote_counter.items()
            if votes >= min_votes
        ]

        scored.sort(key=lambda x: (-x[1][0], -x[1][1], x[0]))

        return [word for word, _ in scored[:top_k]]

if __name__ == "__main__":
    vocab_file = r"C:\Users\USER\Desktop\AdvDS FP\AdvDS-Final-Project\baseline\testcase\words_alpha.txt"
    suggester = Top3HLLSuggester(vocab_file, b=4, q=2)
    test_words = ["applw", "definately", "teh", "recieve", "tommorrow"]
    for word in test_words:
        print(f"Query: {word} -> Suggestions: {suggester.suggest(word)}")