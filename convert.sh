#!/bin/bash

## Example:
## (1) Create "datasets" directory
## (2) Run the cmd "./convert.sh datasets/reviews_sample.json.gz"

INPUT_FILE="$1"
if [ -z "$INPUT_FILE" ]; then # the input file string is zero-length.
	echo "Usage: ./process.py <amazon_input_file>"
	exit
elif ! [[ $INPUT_FILE =~ \.json.gz$ ]]; then
	echo "Only json.gz supported"
	exit
fi

BASE_NAME=${INPUT_FILE%%.*}
DICT_EXT=".dict"
OUTPUT_EXT=".tns"

PRODUCTS_DICT="$BASE_NAME""_asin""$DICT_EXT"
REVIEWERS_DICT="$BASE_NAME""_reviewers""$DICT_EXT"
VOCABULARY_DICT="$BASE_NAME""_vocabulary""$DICT_EXT"
OUTPUT_FILE="$BASE_NAME""$OUTPUT_EXT"

echo "INPUT_FILE: $INPUT_FILE"
echo "PRODUCTS_DICT: $PRODUCTS_DICT"
echo "REVIEWERS_DICT: $REVIEWERS_DICT"
echo "VOCABULARY_DICT: $VOCABULARY_DICT"
echo "OUTPUT_FILE: $OUTPUT_FILE"

## Generate the dictionary files
echo "Reading input file ($INPUT_FILE)"

# echo "Generating product dictionary ($PRODUCTS_DICT)"
# echo "./process.py --infile $INPUT_FILE --outfile $PRODUCTS_DICT --informat
# amazon.json --outformat dictionary --dictfield asin --convert"
# ./process.py --infile $INPUT_FILE --outfile $PRODUCTS_DICT --informat amazon.json --outformat dictionary --dictfield asin --convert

# echo "Generating reviewer dictionary ($REVIEWERS_DICT)"
# echo "./process.py --infile $INPUT_FILE --outfile $REVIEWERS_DICT --informat
# amazon.json --outformat dictionary --dictfield reviewerID --convert"
# ./process.py --infile $INPUT_FILE --outfile $REVIEWERS_DICT --informat amazon.json --outformat dictionary --dictfield reviewerID --convert

echo "Generating vocabulary dictionary ($VOCABULARY_DICT)"
# echo "./process.py --infile $INPUT_FILE --outfile $VOCABULARY_DICT --informat
# amazon.json --outformat dictionary --dictfield reviewText --textfield --convert"
./process.py --infile $INPUT_FILE --outfile $VOCABULARY_DICT --informat amazon.json --outformat dictionary --dictfield reviewText --textfield --convert

## Generate the tensor file
echo "Generating output tensor file ..."
# echo "./process.py --infile $INPUT_FILE --outfile $OUTPUT_FILE --products
# $PRODUCTS_DICT --reviewers $REVIEWERS_DICT --vocabulary $VOCABULARY_DICT
# --informat amazon.json --outformat tensor --convert"
./process.py --infile $INPUT_FILE --outfile $OUTPUT_FILE --products $PRODUCTS_DICT --reviewers $REVIEWERS_DICT --vocabulary $VOCABULARY_DICT --informat amazon.json --outformat tensor --convert

# jli: Do not need to summarize
echo "Done. Summarizing the output tensor file."
## Summarize the tensor output
# echo "./process.py --summarize --infile $OUTPUT_FILE"
./process.py --summarize --infile $OUTPUT_FILE

