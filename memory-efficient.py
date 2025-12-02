import argparse
import subprocess
import time
import tracemalloc
from typing import List, Tuple


GAP_COST = 30


ALPHA = {
	'A': {'A': 0,   'C': 110, 'G': 48,  'T': 94},
	'C': {'A': 110, 'C': 0,   'G': 118, 'T': 48},
	'G': {'A': 48,  'C': 118, 'G': 0,   'T': 110},
	'T': {'A': 94,  'C': 48,  'G': 110, 'T': 0},
}

def mismatch_cost(a: str, b: str) -> int:
	"""Return mismatch cost α_{ab} using the provided matrix.
	If characters are not one of A/C/G/T, fall back to 0 on exact match else 1."""
	if a in ALPHA and b in ALPHA[a]:
		return ALPHA[a][b]
	return 0 if a == b else 1


def _nw_cost_vector(x: str, y: str) -> List[int]:
	"""Compute the last column (costs vs all prefixes of y) of the
	Needleman–Wunsch DP table for strings x and y using O(len(y)) memory.

	Returns a vector v such that v[j] is the optimal alignment cost of x vs y[:j].
	"""
	n = len(y)
	prev = list(range(n + 1))  # aligning empty x vs y prefixes: j * GAP_COST
	# initialize with gap cost
	for j in range(n + 1):
		prev[j] = j * GAP_COST

	for i in range(1, len(x) + 1):
		curr = [0] * (n + 1)
		curr[0] = i * GAP_COST  # x[:i] vs empty y
		for j in range(1, n + 1):
			cost_match = prev[j - 1] + mismatch_cost(x[i - 1], y[j - 1])
			cost_gap_x = prev[j] + GAP_COST  # gap in x (delete x[i-1])
			cost_gap_y = curr[j - 1] + GAP_COST  # gap in y (insert gap for y[j-1])
			curr[j] = min(cost_match, cost_gap_x, cost_gap_y)
		prev = curr
	return prev


def _nw_align_small(x: str, y: str) -> Tuple[str, str]:
	"""Align small strings using full DP (Needleman–Wunsch) to construct alignment.
	Used as base case for Hirschberg when one string is very small.
	"""
	m, n = len(x), len(y)
	dp = [[0] * (n + 1) for _ in range(m + 1)]
	ptr = [[None] * (n + 1) for _ in range(m + 1)]  # 'D' diag, 'U' up, 'L' left

	for i in range(m + 1):
		dp[i][0] = i * GAP_COST
		if i > 0:
			ptr[i][0] = 'U'
	for j in range(n + 1):
		dp[0][j] = j * GAP_COST
		if j > 0:
			ptr[0][j] = 'L'

	for i in range(1, m + 1):
		for j in range(1, n + 1):
			costs = (
				dp[i - 1][j - 1] + mismatch_cost(x[i - 1], y[j - 1]),  # diag
				dp[i - 1][j] + GAP_COST,  # up (gap in y)
				dp[i][j - 1] + GAP_COST,  # left (gap in x)
			)
			best = min(costs)
			dp[i][j] = best
			if best == costs[0]:
				ptr[i][j] = 'D'
			elif best == costs[1]:
				ptr[i][j] = 'U'
			else:
				ptr[i][j] = 'L'

	# traceback
	i, j = m, n
	ax, ay = [], []
	while i > 0 or j > 0:
		if i > 0 and j > 0 and ptr[i][j] == 'D':
			ax.append(x[i - 1])
			ay.append(y[j - 1])
			i -= 1
			j -= 1
		elif i > 0 and ptr[i][j] == 'U':
			ax.append(x[i - 1])
			ay.append('_')
			i -= 1
		else:  # 'L'
			ax.append('_')
			ay.append(y[j - 1])
			j -= 1

	return ''.join(reversed(ax)), ''.join(reversed(ay))


def hirschberg(x: str, y: str) -> Tuple[str, str]:
	"""Hirschberg's algorithm: memory-efficient global alignment.
	Returns a pair of aligned strings (with '-' as gap).
	"""
	m, n = len(x), len(y)
	if m == 0:
		return '_' * n, y
	if n == 0:
		return x, '_' * m
	if m == 1 or n == 1:
		return _nw_align_small(x, y)

	mid = m // 2
	# forward costs for x[:mid] vs y[:j]
	fwd = _nw_cost_vector(x[:mid], y)
	# backward costs for reversed x[mid:] vs reversed y
	bwd = _nw_cost_vector(x[mid:][::-1], y[::-1])

	# find split point q minimizing fwd[q] + bwd[n - q]
	min_cost = None
	split_q = 0
	for q in range(n + 1):
		cost = fwd[q] + bwd[n - q]
		if min_cost is None or cost < min_cost:
			min_cost = cost
			split_q = q

	left_x, left_y = hirschberg(x[:mid], y[:split_q])
	right_x, right_y = hirschberg(x[mid:], y[split_q:])
	return left_x + right_x, left_y + right_y


def alignment_cost(ax: str, ay: str) -> int:
	"""Compute total cost of an alignment with the defined cost model."""
	assert len(ax) == len(ay)
	total = 0
	for a, b in zip(ax, ay):
		if a == '_' or b == '_':
			total += GAP_COST
		else:
			total += mismatch_cost(a, b)
	return total


def read_strings_from_file(path: str) -> Tuple[str, str]:
	with open(path, 'r', encoding='utf-8') as f:
		lines = [line.strip() for line in f.readlines() if line.strip() != '']
	if len(lines) < 2:
		raise ValueError("string.txt must contain two non-empty lines (X and Y)")
	return lines[0], lines[1]


def run_generator(input_path: str) -> Tuple[str, str]:
	"""Run Generator.py with the given input file and parse its stdout as two lines.
	Falls back to reading `string.txt` if stdout doesn't contain two lines."""
	try:
		proc = subprocess.run(
			['python', './Generator.py', input_path],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			check=False,
		)
		out_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
		if len(out_lines) >= 2:
			return out_lines[0], out_lines[1]
	except FileNotFoundError:
		# Python or script not found; fallback
		pass
	# Fallback: use string.txt in workspace
	return read_strings_from_file('string.txt')


def main():
	parser = argparse.ArgumentParser(description='Memory-efficient sequence alignment (Hirschberg)')
	parser.add_argument('input_file', help='Input file path passed to Generator.py')
	parser.add_argument('output_file', help='Output file path to write aligned strings and cost')
	args = parser.parse_args()

	x, y = run_generator(args.input_file)

	# Measure runtime and memory (Python allocations) for alignment
	tracemalloc.start()
	t0 = time.perf_counter()
	ax, ay = hirschberg(x, y)
	t1 = time.perf_counter()
	current_bytes, peak_bytes = tracemalloc.get_traced_memory()
	tracemalloc.stop()

	cost = alignment_cost(ax, ay)
	runtime_ms = (t1 - t0) * 1000.0
	memory_kb = peak_bytes / 1024.0
	# Write outputs to specified file
	with open(args.output_file, 'w', encoding='utf-8') as f:
		# Write only outputs, no labels, in order:
		# Cost, First string alignment, Second string alignment, Time taken (ms), Memory used (KB)
		f.write(f"{cost}\n")
		f.write(f"{ax}\n")
		f.write(f"{ay}\n")
		f.write(f"{runtime_ms:.3f}\n")
		f.write(f"{memory_kb:.3f}\n")

	# Also print a brief summary to stdout
	print(f"Wrote alignment to {args.output_file}")


if __name__ == '__main__':
	main()

