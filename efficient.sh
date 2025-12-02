#!/usr/bin/env zsh
# Wrapper to run the memory-efficient alignment
# Usage: ./efficient.sh <input_file> <output_file>

# Fail fast
set -e
set -u
set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <input_file> <output_file>"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

# Ensure output directory exists
OUT_DIR="$(dirname "$OUTPUT_FILE")"
mkdir -p "$OUT_DIR"

# Run the Python alignment (Generator.py is called inside memory-efficient.py)
python "$SCRIPT_DIR/memory-efficient.py" "$INPUT_FILE" "$OUTPUT_FILE"

echo "Done. Wrote alignment to $OUTPUT_FILE"
