# Dataset Comparison Tool

This suite of tools facilitates the comparison of two datasets based on specific matching criteria, while preserving data privacy through hashing.

## Setup

1. Ensure Python 3 and pip are installed.
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Data Generation

Generate two sample datasets:

```bash
python generate_data.py
```

This will generate `dataset1.csv` and `dataset2.csv` in your working directory.

### Hashing Datasets

Hash a dataset with named arguments for the input and output files:

```bash
python hash_datasets.py --input-file dataset1.csv --output-file hashed_dataset1.csv
python hash_datasets.py --input-file dataset2.csv --output-file hashed_dataset2.csv
```

This generates `hashed_dataset1.csv` and `hashed_dataset2.csv`, containing the hashes for each dataset, respectively.

### Matching Hashes

Compare the hashed datasets by specifying their files with named arguments. Optionally, specify an output file to write the matched hashes:

```bash
python match_hashes.py --hashed-file-1 hashed_dataset1.csv --hashed-file-2 hashed_dataset2.csv --output-file matched_hashes.csv
```

Without `--output-file`, the script will print the count of matches. With `--output-file`, it writes the matched hashes to the specified file.

## Understanding Results

- **Phone Matches:** Entries matching by at least one phone number.
- **Personal Info Matches:** Entries matching by city, state, last name, and the first initial of the first name.
