#!/bin/bash

# Script to run the MiniZinc model with generated instances

# Define directories
DATA_DIR="instancias_minizinc"
RESULTS_DIR="resultados"

# Create results directory if it doesn't exist
mkdir -p $RESULTS_DIR

# Loop through all .dzn files in the data directory
for dzn_file in $DATA_DIR/*.dzn; do
    # Extract the base name of the file (without extension)
    base_name=$(basename "$dzn_file" .dzn)
    
    # Run the MiniZinc model with the current data file
    minizinc pipeline.mzn "$dzn_file" -o "$RESULTS_DIR/${base_name}_result.txt"
done

echo "All instances have been processed."