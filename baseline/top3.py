from collections import defaultdict, Counter
from pathlib import Path
from fuzzyMatcher import FuzzyMatcher


def load_vocab_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        vocab = [line.strip().lower() for line in f if line.strip()]
    return vocab


class Top3Suggester:
    def __init__(self, vocab, st=0.75, m=4, q=2, k=3):
        if isinstance(vocab, (str, Path)):
            vocab = load_vocab_from_file(vocab)
        self.fm = FuzzyMatcher(st=st, m=m, q=q, k=k)
        self.segment_to_words = defaultdict(set)
        total = len(vocab)
        for idx, word in enumerate(vocab):
            if idx % 10000 == 0 and idx > 0:
                print(f"[INFO] 已載入 {idx}/{total} 個詞")
            for seg in self.fm.segmenter.encode_and_segment(word):
                fp = seg.to01()
                self.segment_to_words[fp].add(word)
            self.fm.insert(word)
        self.vocab = set(vocab)
        self.m = m

    def suggest(self, word, top_k=3, min_votes=1):
        segs = [seg.to01() for seg in self.fm.segmenter.encode_and_segment(word)]
        vote_counter = Counter()
        for seg in segs:
            for w in self.segment_to_words.get(seg, []):
                vote_counter[w] += 1
        scored = [
            (w, votes / self.m)
            for w, votes in vote_counter.items()
            if votes >= min_votes
        ]
        scored.sort(key=lambda x: (-x[1], x[0]))
        return [w for w, _ in scored[:top_k]] if scored else []


if __name__ == "__main__":
    vocab_file = r"C:\Users\USER\Desktop\AdvDS FP\AdvDS-Final-Project\baseline\testcase\words_alpha.txt"
    suggester = Top3Suggester(vocab_file)
    test_words = ["applw", "definately", "teh", "recieve", "tommorrow"]
    for word in test_words:
        print(f"Query: {word} -> Suggestions: {suggester.suggest(word)}")
