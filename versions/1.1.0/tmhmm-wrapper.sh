#!/bin/bash

# TMHMM Docker Wrapper Script for macOS ARM64
# This script provides a convenient way to run TMHMM using Docker

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if the TMHMM Docker image exists
if ! docker image inspect ss93/tmhmm > /dev/null 2>&1; then
    echo "Error: TMHMM Docker image not found. Please run: docker pull ss93/tmhmm"
    exit 1
fi

# Create a temporary directory for input/output files
TEMP_DIR=$(mktemp -d)
INPUT_FILE=""
OUTPUT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            INPUT_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "TMHMM Docker Wrapper for macOS"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -f, --file FILE     Input FASTA file"
            echo "  -o, --output FILE   Output file (optional)"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 -f input.fasta -o output.txt"
            echo ""
            echo "Note: This wrapper uses Docker to run TMHMM on macOS ARM64"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check if input file is provided
if [[ -z "$INPUT_FILE" ]]; then
    echo "Error: Input file is required. Use -f or --file to specify the input FASTA file."
    echo "Use -h or --help for usage information"
    exit 1
fi

# Check if input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file '$INPUT_FILE' does not exist."
    exit 1
fi

# Copy input file to temporary directory
cp "$INPUT_FILE" "$TEMP_DIR/input.fasta"

# Set output file name if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
    OUTPUT_FILE="${INPUT_FILE%.*}_tmhmm_output.txt"
fi

# Run TMHMM in Docker container
echo "Running TMHMM on file: $INPUT_FILE"
echo "Output will be saved to: $OUTPUT_FILE"

docker run --rm \
    -v "$TEMP_DIR:/data" \
    -v "$(pwd):/workspace" \
    ss93/tmhmm \
    tmhmm /data/input.fasta > "$OUTPUT_FILE"

# Check if the command was successful
if [[ $? -eq 0 ]]; then
    echo "TMHMM analysis completed successfully!"
    echo "Results saved to: $OUTPUT_FILE"
else
    echo "Error: TMHMM analysis failed."
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up temporary directory
rm -rf "$TEMP_DIR"

echo "Analysis complete!"
