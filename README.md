# Private Set Intersection Script

This project contains scripts for privacy-preserving set intersection, allowing two datasets to be compared without revealing the full contents.

## Features

- Hash sensitive data (names, addresses, phone numbers, emails) for privacy
- Match records across datasets using hashed identifiers
- Support for up to 3 phone numbers per record
- Validate and standardize phone numbers using libphonenumber
- Match phones across any position between datasets

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install pre-commit:
   ```
   pre-commit install
   ```

## Using pre-commit

This project uses pre-commit to enforce code quality standards. When you commit changes, pre-commit will automatically:

- Format Python code with Black
- Sort imports with isort
- Lint code with Ruff
- Check types with mypy
- Fix common issues like trailing whitespace

If any checks fail, the commit will be blocked until the issues are fixed. Many issues are fixed automatically.

To run pre-commit manually on all files:
```
pre-commit run --all-files
```

## Usage

### Hashing a dataset

```
python hash_datasets.py --input-file your_data.csv --output-file hashed_data.csv --debug
```

This script processes an input CSV file, normalizes and hashes specified fields (phone numbers, email, and a concatenation of name/address components), and outputs a new CSV with the pseudonym and these hashed values.

**Optional: Dumping Bad Phone Records**

You can also specify an optional file path to dump records that contain phone numbers that could not be successfully standardized. This is useful for identifying and correcting data quality issues in the source file.

```
python hash_datasets.py --input-file your_data.csv --output-file hashed_data.csv --bad-records-file problematic_phone_records.csv
```

The `problematic_phone_records.csv` will contain the following columns in plain text:
- `Pseudonym`: The original pseudonym.
- `OriginalPhoneInput`: The exact phone number string that caused an issue.
- `PhoneFieldLabel`: The name of the phone field (e.g., `md_us_phone_1`).
- `ReasonForFailure`: A description of why the phone number could not be standardized (e.g., blank, invalid, parsing error).
- All other columns from the original input row will also be included to provide full context.

### Finding matches between datasets

```
python match_hashes.py --hashed-file-1 hashed_data1.csv --hashed-file-2 hashed_data2.csv --output-file matches.csv
```

## CSV Format

Input files should be CSV files with columns for:
- pseudonym/uniqueid/index
- name fields (first name, last name)
- address fields (city, state)
- phone numbers (up to 3)
- email

The scripts will attempt to find these columns using common naming patterns.
