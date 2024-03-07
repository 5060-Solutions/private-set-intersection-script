# Dataset Comparison Tool

This suite of tools facilitates the comparison of two datasets based on specific matching criteria, including phone numbers, personal information, and email addresses, while preserving data privacy through hashing. Pseudonyms are kept clear for identification.

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

This will generate `dataset1.csv` and `dataset2.csv` in your working directory, ready for hashing and matching.

### Hashing Datasets

Hash the datasets, keeping pseudonyms unencrypted, with named arguments for the input and output files:

```bash
python hash_datasets.py --input-file dataset1.csv --output-file hashed_dataset1.csv
python hash_datasets.py --input-file dataset2.csv --output-file hashed_dataset2.csv
```

This process generates `hashed_dataset1.csv` and `hashed_dataset2.csv`, containing the hashes for each dataset, respectively, with pseudonyms and email hashes included.

### Matching Hashes

Compare the hashed datasets, optionally outputting the matched hashes and pseudonyms to a specified file:

```bash
python match_hashes.py --hashed-file-1 hashed_dataset1.csv --hashed-file-2 hashed_dataset2.csv --output-file matched_hashes.csv
```

With `--output-file`, it writes the matched hashes, including pseudonyms for identification, to the specified file. It will always print the result counts to the console.

## Understanding Results

- **Phone Matches:** Entries matching by at least one phone number.
- **Personal Info Matches:** Entries matching by city, state, last name, and the first initial of the first name.
- **Email Matches:** Entries with matching email addresses.
