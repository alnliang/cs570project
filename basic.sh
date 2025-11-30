#!/bin/bash

# Usage check
if [ $# -ne 2 ]; then
    echo "Usage: ./basic.sh <input_file> <output_file>"
    exit 1
fi

INPUT=$1
OUTPUT=$2

# Run basic.py with the provided arguments
# Using python3 first; if not found, fallback to python
if command -v python3 &> /dev/null; then
    python3 basic.py "$INPUT" "$OUTPUT"
else
    python basic.py "$INPUT" "$OUTPUT"
fi