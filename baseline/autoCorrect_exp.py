# autoCorrector.py
from difflib import get_close_matches
from fuzzyMatcher import FuzzyMatcher
from top3 import Top3Suggester


def load_words_from_file(filepath: str) -> list[str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def save_suggestions_to_file(suggestions: list[str], filepath: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        for word in suggestions:
            f.write(word + '\n')


# === CONFIG FILE PATHS ===
vocab_file_path = "testcase/database3.txt"     # Input file with vocab words (one per line)
query_file_path = "testcase/typo_file.txt"     # Input file with words to query
output_file_path = "testcase/suggestion.txt"  # Output file for suggestions

# === LOAD DATA ===
vocab_words = load_words_from_file(vocab_file_path)
query_words = load_words_from_file(query_file_path)

# === INIT MODULES ===
autocorrector = FuzzyMatcher()
suggester = Top3Suggester(vocab_words)

for word in vocab_words:
    autocorrector.insert(word)

# === PROCESS QUERIES ===
suggestions = []

for word in query_words:
    if autocorrector.should_autocorrect(word):
        top = suggester.suggest(word)
        suggestions.append(top[0] if top else "")
    else:
        suggestions.append(word)  # Keep the original if no correction needed

# === WRITE OUTPUT ===
save_suggestions_to_file(suggestions, output_file_path)
print(f"Suggestions saved to: {output_file_path}")
