import csv
import argparse

def load_hashes(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

def find_matches(hashes1, hashes2):
    match_counts = {'Phone': 0, 'Personal Info': 0, 'Email': 0}
    phone_map1 = {(row['Phone Hash 1'], row['Phone Hash 2']): row['Pseudonym'] for row in hashes1}
    phone_map2 = {(row['Phone Hash 1'], row['Phone Hash 2']): row['Pseudonym'] for row in hashes2}
    personal_info_map1 = {row['Personal Info Hash']: row['Pseudonym'] for row in hashes1}
    personal_info_map2 = {row['Personal Info Hash']: row['Pseudonym'] for row in hashes2}
    email_map1 = {row['Email Hash']: row['Pseudonym'] for row in hashes1}
    email_map2 = {row['Email Hash']: row['Pseudonym'] for row in hashes2}

    for key in phone_map1:
        if key in phone_map2:
            match_counts['Phone'] += 1
    
    for key in personal_info_map1:
        if key in personal_info_map2:
            match_counts['Personal Info'] += 1
    
    for key in email_map1:
        if key in email_map2:
            match_counts['Email'] += 1

    return match_counts

def main():
    parser = argparse.ArgumentParser(description='Match two hashed datasets and output detailed common entries.')
    parser.add_argument('--hashed-file-1', type=str, required=True, help='Path to the first hashed dataset')
    parser.add_argument('--hashed-file-2', type=str, required=True, help='Path to the second hashed dataset')
    parser.add_argument('--output-file', type=str, required=True, help='Path to output file for detailed matched entries')
    args = parser.parse_args()

    hashes1 = load_hashes(args.hashed_file_1)
    hashes2 = load_hashes(args.hashed_file_2)
    match_counts = find_matches(hashes1, hashes2)

    with open(args.output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Match Type', 'Count'])
        for match_type, count in match_counts.items():
            writer.writerow([match_type, count])

    total_matches = sum(match_counts.values())
    print(f"Total Matches Found: {total_matches}")
    for match_type, count in match_counts.items():
        print(f"{match_type} Matches: {count}")

if __name__ == "__main__":
    main()
