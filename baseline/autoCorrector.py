# autoCorrector.py
from difflib import get_close_matches
from fuzzyMatcher import FuzzyMatcher
from top3 import Top3Suggester

autocorrector = FuzzyMatcher()


# dummy linear search for the closest word
def get_correction(word, vocabulary, n=1, cutoff=0.8):
    """
    Returns the top candidate from vocabulary similar to the input word.
    """
    candidates = get_close_matches(word, vocabulary, n=n, cutoff=cutoff)
    return candidates[0] if candidates else None

# vocab_file = r"C:\Users\USER\Desktop\AdvDS FP\AdvDS-Final-Project\baseline\testcase\words_alpha.txt"
# suggester = Top3Suggester(vocab_file)

# Simple simulate user input
vocab_file = ["hello", "hello", "helo", "heloo"]
suggester = Top3Suggester(vocab_file)

for text in vocab_file:
    autocorrector.insert(text)


# Query
print("Should autocorrect 'helioo'? ", autocorrector.should_autocorrect("helioo"))
# suggestion = get_correction("helioo", vocabulary)
if autocorrector.should_autocorrect("helioo"):
    suggestion = suggester.suggest("helioo")
    print(f"Suggestion: {suggestion[0]}")


# Future AutoCorrection flow
"""
while input:
    if autocorrector.should_autocorrect(input):
        suggestion = get_correction(input, vocabulary)
        print(f"Did you mean '{suggestion}'?")
    else:
        print("Word accepted.")
"""
