import csv
import argparse

def load_hashes(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

def find_matches(hashes1, hashes2):
    matched_entries = []

    # Mapping for easier access to hashes
    phone_map1 = {(row['Phone Hash 1'], row['Phone Hash 2']): row['Pseudonym'] for row in hashes1}
    phone_map2 = {(row['Phone Hash 1'], row['Phone Hash 2']): row['Pseudonym'] for row in hashes2}
    personal_info_map1 = {row['Personal Info Hash']: row['Pseudonym'] for row in hashes1}
    personal_info_map2 = {row['Personal Info Hash']: row['Pseudonym'] for row in hashes2}
    email_map1 = {row['Email Hash']: row['Pseudonym'] for row in hashes1}
    email_map2 = {row['Email Hash']: row['Pseudonym'] for row in hashes2}

    # Check for phone matches
    for key in phone_map1:
        if key in phone_map2:
            matched_entries.append(('Phone', phone_map1[key], phone_map2[key]))
    
    # Check for personal info matches
    for key in personal_info_map1:
        if key in personal_info_map2:
            matched_entries.append(('Personal Info', personal_info_map1[key], personal_info_map2[key]))
    
    # Check for email matches
    for key in email_map1:
        if key in email_map2:
            matched_entries.append(('Email', email_map1[key], email_map2[key]))

    return matched_entries

def main():
    parser = argparse.ArgumentParser(description='Match two hashed datasets and output detailed common entries.')
    parser.add_argument('--hashed-file-1', type=str, required=True, help='Path to the first hashed dataset')
    parser.add_argument('--hashed-file-2', type=str, required=True, help='Path to the second hashed dataset')
    parser.add_argument('--output-file', type=str, help='Optional: Path to output file for detailed matched entries')
    args = parser.parse_args()

    hashes1 = load_hashes(args.hashed_file_1)
    hashes2 = load_hashes(args.hashed_file_2)
    matched_entries = find_matches(hashes1, hashes2)

    if args.output_file:
        with open(args.output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Match Type', 'Pseudonym from File 1', 'Pseudonym from File 2'])
            for match_type, pseudo1, pseudo2 in matched_entries:
                writer.writerow([match_type, pseudo1, pseudo2])

    print(f"Total Matches Found: {len(matched_entries)}")
    for match_type, pseudo1, pseudo2 in matched_entries:
        print(f"Match Type: {match_type}, Pseudonym from File 1: {pseudo1}, Pseudonym from File 2: {pseudo2}")

if __name__ == "__main__":
    main()
