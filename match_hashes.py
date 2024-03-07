import csv
import argparse

def load_hashes(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

def find_matches(hashes1, hashes2):
    phone_hashes1 = {h for record in hashes1 for h in record[:2]}
    phone_hashes2 = {h for record in hashes2 for h in record[:2]}
    personal_info_hashes1 = {record[2] for record in hashes1}
    personal_info_hashes2 = {record[2] for record in hashes2}

    phone_matches = phone_hashes1.intersection(phone_hashes2)
    personal_info_matches = personal_info_hashes1.intersection(personal_info_hashes2)
    
    return phone_matches, personal_info_matches

def main():
    parser = argparse.ArgumentParser(description='Match two hashed datasets and find common entries.')
    parser.add_argument('--hashed-file-1', type=str, required=True, help='Path to the first hashed CSV file')
    parser.add_argument('--hashed-file-2', type=str, required=True, help='Path to the second hashed CSV file')
    parser.add_argument('--output-file', type=str, help='Optional: Path for the output CSV file containing the matched hashes')

    args = parser.parse_args()

    hashes1 = load_hashes(args.hashed_file_1)
    hashes2 = load_hashes(args.hashed_file_2)
    phone_matches, personal_info_matches = find_matches(hashes1, hashes2)

    if args.output_file:
        with open(args.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Matched Phone Hashes'])
            writer.writerows([[match] for match in phone_matches])
            writer.writerow(['Matched Personal Info Hashes'])
            writer.writerows([[match] for match in personal_info_matches])

    print(f"Phone Matches: {len(phone_matches)}")
    print(f"Personal Info Matches: {len(personal_info_matches)}")

if __name__ == "__main__":
    main()
