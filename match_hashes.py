import argparse
import csv
import itertools
from typing import Any, Dict, List, Tuple

from tqdm import tqdm


def load_hashes(file_path: str) -> List[Dict[str, str]]:
    """
    Load hashed data from a CSV file.

    Args:
        file_path: Path to the CSV file containing hashed data

    Returns:
        List of dictionaries, each representing a row in the CSV
    """
    try:
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []


def find_and_write_matches(hashes1: List[Dict[str, str]], hashes2: List[Dict[str, str]], output_file: str) -> None:
    """
    Find matching records between two datasets and write results to file.

    Args:
        hashes1: First dataset with hashed identifiers
        hashes2: Second dataset with hashed identifiers
        output_file: Path to output CSV file for match results
    """
    matched_entries: Dict[Tuple[str, str], Dict[str, Any]] = {}

    # Create phone hash mapping for dataset 1
    phone_map1: Dict[str, List[Dict[str, str]]] = {}
    for row in hashes1:
        phones = []
        if row["Phone Hash 1"]:
            phones.append(row["Phone Hash 1"])
        if row["Phone Hash 2"]:
            phones.append(row["Phone Hash 2"])
        if "Phone Hash 3" in row and row["Phone Hash 3"]:
            phones.append(row["Phone Hash 3"])

        for phone in phones:
            phone_map1.setdefault(phone, []).append(row)

    # Create phone hash mapping for dataset 2
    phone_map2: Dict[str, List[Dict[str, str]]] = {}
    for row in hashes2:
        phones = []
        if row["Phone Hash 1"]:
            phones.append(row["Phone Hash 1"])
        if row["Phone Hash 2"]:
            phones.append(row["Phone Hash 2"])
        if "Phone Hash 3" in row and row["Phone Hash 3"]:
            phones.append(row["Phone Hash 3"])

        for phone in phones:
            phone_map2.setdefault(phone, []).append(row)

    # Create maps for other identifying information
    personal_info_map1 = {row["Personal Info Hash"]: row for row in hashes1 if row["Personal Info Hash"]}
    personal_info_map2 = {row["Personal Info Hash"]: row for row in hashes2 if row["Personal Info Hash"]}
    email_map1 = {row["Email Hash"]: row for row in hashes1 if row["Email Hash"]}
    email_map2 = {row["Email Hash"]: row for row in hashes2 if row["Email Hash"]}

    # Find phone matches across any position
    for phone_hash, rows1 in tqdm(phone_map1.items(), desc="Matching phone hashes", unit="hash"):
        if phone_hash in phone_map2:
            rows2 = phone_map2[phone_hash]
            for row1, row2 in itertools.product(rows1, rows2):
                pseudonyms = (row1["Pseudonym"], row2["Pseudonym"])
                hash_pair = matched_entries.get(
                    pseudonyms,
                    {
                        "Phone Match": "No",
                        "Email Match": "No",
                        "Personal Info Match": "No",
                        "Matched Phone Hashes": set(),
                    },
                )

                if hash_pair["Phone Match"] == "No":
                    hash_pair["Phone Match"] = "Yes"
                    hash_pair["Matched Phone Hashes"] = set()

                hash_pair["Matched Phone Hashes"].add(phone_hash)
                matched_entries[pseudonyms] = hash_pair

    # Find email matches
    for key, value in tqdm(email_map1.items(), desc="Matching email hashes", unit="record"):
        if key in email_map2:
            pseudonyms = (value["Pseudonym"], email_map2[key]["Pseudonym"])
            hash_pair = matched_entries.get(
                pseudonyms,
                {
                    "Phone Match": "No",
                    "Email Match": "No",
                    "Personal Info Match": "No",
                    "Matched Phone Hashes": set(),
                    "Matched Email Hash": "",
                },
            )
            hash_pair["Email Match"] = "Yes"
            hash_pair["Matched Email Hash"] = key
            matched_entries[pseudonyms] = hash_pair

    # Find personal info matches
    for key, value in tqdm(personal_info_map1.items(), desc="Matching personal info hashes", unit="record"):
        if key in personal_info_map2:
            pseudonyms = (value["Pseudonym"], personal_info_map2[key]["Pseudonym"])
            hash_pair = matched_entries.get(
                pseudonyms,
                {
                    "Phone Match": "No",
                    "Email Match": "No",
                    "Personal Info Match": "No",
                    "Matched Phone Hashes": set(),
                    "Matched Personal Info Hash": "",
                    "Matched Email Hash": "",
                },
            )
            hash_pair["Personal Info Match"] = "Yes"
            hash_pair["Matched Personal Info Hash"] = key
            matched_entries[pseudonyms] = hash_pair

    # Write results to output file
    try:
        with open(output_file, "w", newline="") as file:
            writer = csv.writer(file)
            # Update header for flexible phone matching
            writer.writerow(
                [
                    "Pseudonym1",
                    "Pseudonym2",
                    "Phone Match",
                    "Email Match",
                    "Personal Info Match",
                    "Matched Phone Hashes",
                    "Matched Personal Info Hash",
                    "Matched Email Hash",
                ]
            )

            for pseudonyms, matches in matched_entries.items():
                # Convert phone hash set to string for output
                phone_hashes = (
                    "|".join(matches.get("Matched Phone Hashes", set())) if "Matched Phone Hashes" in matches else ""
                )
                writer.writerow(
                    [
                        pseudonyms[0],
                        pseudonyms[1],
                        matches["Phone Match"],
                        matches["Email Match"],
                        matches["Personal Info Match"],
                        phone_hashes,
                        matches.get("Matched Personal Info Hash", ""),
                        matches.get("Matched Email Hash", ""),
                    ]
                )
    except IOError:
        print(f"Error writing to output file: {output_file}")
        return

    # Print summary statistics
    print("Matched entries written to output file.")
    total_matches = len(matched_entries)
    print(f"Total unique matched pairs: {total_matches}")
    for match_type in ["Phone Match", "Email Match", "Personal Info Match"]:
        count = sum(1 for matches in matched_entries.values() if matches[match_type] == "Yes")
        print(f"{match_type}: {count}")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Match two hashed datasets and output detailed common entries.")
    parser.add_argument("--hashed-file-1", type=str, required=True, help="Path to the first hashed dataset")
    parser.add_argument("--hashed-file-2", type=str, required=True, help="Path to the second hashed dataset")
    parser.add_argument(
        "--output-file",
        type=str,
        required=True,
        help="Path to output file for detailed matched entries",
    )
    args = parser.parse_args()

    hashes1 = load_hashes(args.hashed_file_1)
    hashes2 = load_hashes(args.hashed_file_2)

    if not hashes1 or not hashes2:
        print("One or both input files are empty or not found. Aborting.")
        return

    find_and_write_matches(hashes1, hashes2, args.output_file)


if __name__ == "__main__":
    main()
