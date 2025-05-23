from bloomFilter import BloomSegmenter
from cuckooFilter import CuckooFilter
from fuzzyMatcher import FuzzyMatcher

def apply_cuckoo_filter():
    seg = BloomSegmenter(l=128, k=3, m=4, q=2)
    cf = CuckooFilter(num_buckets=8, bucket_size=2, fp_len=16)

    words = ["apple", "banana", "orange", "grape", "mango", "melon", "berry"]
    for w in words:
        for s in seg.encode_and_segment(w):
            cf.insert(s.to01())

    print("Bucket lengths:", cf.bucket_lengths())
    print("Capacity:", cf.capacity, "Stored:", len(cf), "Load:", f"{cf.load_factor():.2%}")

def apply_fuzzy_matcher():
    fm = FuzzyMatcher(st=0.5)

    for w in ["apple", "banana", "grape", "orange", "banana"]:
        fm.insert(w)

    for q in ["applle", "banana", "banan", "orenge", "grap", "pineapple"]:
        sim = fm.query_similarity(q)
        cnt = fm.query_count(q)
        print(f"{q:10s}  sim={sim:4.2f}  count≈{cnt:<2d}  match={fm.is_match(q)}")

    print(fm.stats())

def apply_bloom_filter():
    seg = BloomSegmenter(l=128, k=3, m=4, q=2)
    bitvec = seg.encode("apple")
    segments = seg.segment(bitvec)

    print(f"Full Bloom Vector ({len(bitvec)} bits):\n{bitvec.to01()}")
    print("-" * 60)
    for i, s in enumerate(segments):
        print(f"Segment {i} ({s.count()} ones): {s.to01()}")

if __name__ == "__main__":
    apply_bloom_filter()