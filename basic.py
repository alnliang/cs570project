import sys
import subprocess
import time
import os
import psutil


GAP = 30

ALPHA_MATRIX = {
    'A': {'A': 0,   'C': 110, 'G': 48,  'T': 94},
    'C': {'A': 110, 'C': 0,   'G': 118, 'T': 48},
    'G': {'A': 48,  'C': 118, 'G': 0,   'T': 110},
    'T': {'A': 94,  'C': 48,  'G': 110, 'T': 0},
}


def mismatch(a, b):
    return ALPHA_MATRIX[a][b]

# Basic O(mn) dynamic programming alignment.
def align_basic(s, t):
    m, n = len(s), len(t)

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        dp[i][0] = i * GAP
    for j in range(1, n + 1):
        dp[0][j] = j * GAP

    # Fill DP table
    for i in range(1, m + 1):
        si = s[i - 1]
        for j in range(1, n + 1):
            tj = t[j - 1]

            dp[i][j] = min(
                dp[i - 1][j - 1] + mismatch(si, tj),
                dp[i - 1][j] + GAP,
                dp[i][j - 1] + GAP
            )

    # Backtracking
    i, j = m, n
    as_list = []
    at_list = []

    while i > 0 or j > 0:
        # Case 1: characters align (match/substitute)
        if i > 0 and j > 0:
            si = s[i - 1]
            tj = t[j - 1]
            if dp[i][j] == dp[i - 1][j - 1] + mismatch(si, tj):
                as_list.append(si)
                at_list.append(tj)
                i -= 1
                j -= 1
                continue
        # Case 2: s[i-1] aligned with gap
        if i > 0 and dp[i][j] == dp[i - 1][j] + GAP:
            as_list.append(s[i - 1])
            at_list.append('_')
            i -= 1
        else:
            # Case 3: t[j-1] aligned with gap
            as_list.append('_')
            at_list.append(t[j - 1])
            j -= 1

    as_list.reverse()
    at_list.reverse()

    return dp[m][n], ''.join(as_list), ''.join(at_list)

def get_strings_from_generator(input_file):
    proc = subprocess.Popen(
        [sys.executable, "generator.py", input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate()

    lines = [line.strip() for line in out.split("\n") if line.strip() != ""]
    if len(lines) < 2:
        raise ValueError("generator.py did not output two lines.")

    return lines[0], lines[1]

def get_memory_kb():
    if psutil is None:
        return 0.0
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024.0

def main():
    if len(sys.argv) != 3:
        print("Usage: python basic.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    X, Y = get_strings_from_generator(input_file)


    start_time = time.time()
    start_mem = get_memory_kb()

    cost, aligned_X, aligned_Y = align_basic(X, Y)

    end_time = time.time()
    end_mem = get_memory_kb()

    time_ms = (end_time - start_time) * 1000
    mem_kb = max(end_mem - start_mem, 0.0)


    with open(output_file, 'w') as out:
        out.write(str(cost) + '\n')
        out.write(aligned_X + '\n')
        out.write(aligned_Y + '\n')
        out.write(f"{time_ms:.3f}\n")
        out.write(f"{mem_kb:.3f}\n")


if __name__ == "__main__":
    main()