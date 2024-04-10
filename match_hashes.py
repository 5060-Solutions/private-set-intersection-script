import csv
import argparse
from tqdm import tqdm

def load_hashes(file_path):
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

def find_and_write_matches(hashes1, hashes2, output_file):
    matched_entries = {}
    phone_map1 = {(row['Phone Hash 1'], row['Phone Hash 2']): row for row in hashes1}
    phone_map2 = {(row['Phone Hash 1'], row['Phone Hash 2']): row for row in hashes2}
    personal_info_map1 = {row['Personal Info Hash']: row for row in hashes1}
    personal_info_map2 = {row['Personal Info Hash']: row for row in hashes2}
    email_map1 = {row['Email Hash']: row for row in hashes1}
    email_map2 = {row['Email Hash']: row for row in hashes2}

    for key, value in tqdm(phone_map1.items(), desc="Matching phone hashes", unit="record"):
        reverse_key = (key[1], key[0])
        if key in phone_map2 or reverse_key in phone_map2:
            target_value = phone_map2.get(key) or phone_map2.get(reverse_key)
            pseudonyms = (value['Pseudonym'], target_value['Pseudonym'])
            hash_pair = matched_entries.get(pseudonyms, {'Phone Match': 'No', 'Email Match': 'No', 'Personal Info Match': 'No', 'Matched Phone Hash 1': '', 'Matched Phone Hash 2': '', 'Matched Personal Info Hash': '', 'Matched Email Hash': ''})
            hash_pair['Phone Match'] = 'Yes'
            hash_pair['Matched Phone Hash 1'], hash_pair['Matched Phone Hash 2'] = key
            matched_entries[pseudonyms] = hash_pair

    for key, value in tqdm(email_map1.items(), desc="Matching email hashes", unit="record"):
        if key in email_map2:
            pseudonyms = (value['Pseudonym'], email_map2[key]['Pseudonym'])
            hash_pair = matched_entries.get(pseudonyms, {'Phone Match': 'No', 'Email Match': 'No', 'Personal Info Match': 'No', 'Matched Phone Hash 1': '', 'Matched Phone Hash 2': '', 'Matched Personal Info Hash': '', 'Matched Email Hash': ''})
            hash_pair['Email Match'] = 'Yes'
            hash_pair['Matched Email Hash'] = key
            matched_entries[pseudonyms] = hash_pair

    for key, value in tqdm(personal_info_map1.items(), desc="Matching personal info hashes", unit="record"):
        if key in personal_info_map2:
            pseudonyms = (value['Pseudonym'], personal_info_map2[key]['Pseudonym'])
            hash_pair = matched_entries.get(pseudonyms, {'Phone Match': 'No', 'Email Match': 'No', 'Personal Info Match': 'No', 'Matched Phone Hash 1': '', 'Matched Phone Hash 2': '', 'Matched Personal Info Hash': '', 'Matched Email Hash': ''})
            hash_pair['Personal Info Match'] = 'Yes'
            hash_pair['Matched Personal Info Hash'] = key
            matched_entries[pseudonyms] = hash_pair

    try:
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Pseudonym1', 'Pseudonym2', 'Phone Match', 'Email Match', 'Personal Info Match', 'Matched Phone Hash 1', 'Matched Phone Hash 2', 'Matched Personal Info Hash', 'Matched Email Hash'])
            for pseudonyms, matches in matched_entries.items():
                writer.writerow([pseudonyms[0], pseudonyms[1], matches['Phone Match'], matches['Email Match'], matches['Personal Info Match'], matches.get('Matched Phone Hash 1', ''), matches.get('Matched Phone Hash 2', ''), matches.get('Matched Personal Info Hash', ''), matches.get('Matched Email Hash', '')])
    except IOError:
        print(f"Error writing to output file: {output_file}")
        return

    print("Matched entries written to output file.")
    total_matches = len(matched_entries)
    print(f"Total unique matched pairs: {total_matches}")
    for match_type in ['Phone Match', 'Email Match', 'Personal Info Match']:
        count = sum(1 for matches in matched_entries.values() if matches[match_type] == 'Yes')
        print(f"{match_type}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Match two hashed datasets and output detailed common entries.')
    parser.add_argument('--hashed-file-1', type=str, required=True, help='Path to the first hashed dataset')
    parser.add_argument('--hashed-file-2', type=str, required=True, help='Path to the second hashed dataset')
    parser.add_argument('--output-file', type=str, required=True, help='Path to output file for detailed matched entries')
    args = parser.parse_args()

    hashes1 = load_hashes(args.hashed_file_1)
    hashes2 = load_hashes(args.hashed_file_2)

    if not hashes1 or not hashes2:
        print("One or both input files are empty or not found. Aborting.")
        return

    find_and_write_matches(hashes1, hashes2, args.output_file)

if __name__ == "__main__":
    main()