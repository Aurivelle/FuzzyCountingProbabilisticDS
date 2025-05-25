def compare_files(file1_path, file2_path):
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    total_lines = max(len(lines1), len(lines2))
    diff_lines = sum(1 for a, b in zip(lines1, lines2) if a.strip() != b.strip())
    
    # If one file is longer, count extra lines as different
    diff_lines += abs(len(lines1) - len(lines2))

    print(f"Total lines: {total_lines}")
    print(f"Different lines: {diff_lines}")
    print(f"Difference rate: {diff_lines / total_lines * 100:.2f}%")

# Example usage:
compare_files('testcase/output_compare.txt', 'testcase/corrected_output.txt')
