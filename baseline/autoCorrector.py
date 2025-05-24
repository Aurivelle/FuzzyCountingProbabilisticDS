# autoCorrector.py
from difflib import get_close_matches
from fuzzyMatcher import FuzzyMatcher

autocorrector = FuzzyMatcher()



def get_correction(word, vocabulary, n=1, cutoff=0.8):
    """
    Returns the top candidate from vocabulary similar to the input word.
    """
    candidates = get_close_matches(word, vocabulary, n=n, cutoff=cutoff)
    return candidates[0] if candidates else None

# Simple simulate user input
vocabulary = ["hello", "hello", "helo", "heloo"]

for text in vocabulary:
    autocorrector.insert(text)


# Query
print("Should autocorrect 'helioo'? ", autocorrector.should_autocorrect("helioo"))
suggestion = get_correction("helioo", vocabulary)
print(f"Did you mean '{suggestion}'?")

# Future AutoCorrection flow
"""
while input:
    if autocorrector.should_autocorrect(input):
        suggestion = get_correction(input, vocabulary)
        print(f"Did you mean '{suggestion}'?")
    else:
        print("Word accepted.")
"""
