from pathlib import Path
from typing import List, Optional

from difflib import get_close_matches
from fuzzyMatcher import FuzzyMatcher


class Autocorrector:

    def __init__(
        self,
        vocab: List[str] | Path,
        *,
        st: float = 0.75,
        top_k: int = 3,
    ) -> None:
        self.top_k = top_k
        self.fm = FuzzyMatcher(st=st)

        if isinstance(vocab, Path):
            vocab = [
                w.strip() for w in Path(vocab).read_text().splitlines() if w.strip()
            ]
        self._dict: set[str] = set(vocab)
        for w in vocab:
            self.fm.insert(w)

    def freq(self, word: str) -> int:
        return self.fm.query_count(word)

    def suggest(self, word: str) -> Optional[List[str]]:
        if not self.fm.should_autocorrect(word):
            return None

        return get_close_matches(word, self._dict, n=self.top_k, cutoff=self.fm.st)

    def add_word(self, word: str) -> None:
        if word not in self._dict:
            self._dict.add(word)
            self.fm.insert(word)


if __name__ == "__main__":
    ac = Autocorrector(Path("./testcase/database.txt"), st=0.6, top_k=5)
    tests = ["applle", "banana", "banan", "orenge", "grap", "pineapple"]
    for w in tests:
        print(f"{w:<12}  freq≈{ac.freq(w):<3}  sugg={ac.suggest(w)}")
    print("\nIndex stats:", ac.fm.stats())
