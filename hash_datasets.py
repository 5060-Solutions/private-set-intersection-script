import csv
import hashlib
import argparse

def hash_entry(pseudonym, u_firstname, u_name, u_city, u_state, md_us_phone_1, md_us_phone_2, email):
    phone_hash_1 = hashlib.sha256(md_us_phone_1.encode('utf-8')).hexdigest()
    phone_hash_2 = hashlib.sha256(md_us_phone_2.encode('utf-8')).hexdigest()

    first_letter_firstname = u_firstname[0] if u_firstname else ''
    surname = u_name

    personal_info_concat = f"{u_city}{u_state}{surname}{first_letter_firstname}"
    personal_info_hash = hashlib.sha256(personal_info_concat.encode('utf-8')).hexdigest()
    email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()

    return [pseudonym, phone_hash_1, phone_hash_2, personal_info_hash, email_hash]

def hash_dataset(input_file, output_file):
    with open(input_file, newline='') as csvfile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(outfile)
        writer.writerow(['Pseudonym', 'Phone Hash 1', 'Phone Hash 2', 'Personal Info Hash', 'Email Hash'])
        for row in reader:
            hashed_row = hash_entry(row['pseudonym'], row['u_firstname'], row['u_name'], row['u_city'], row['u_state'], row['md_us_phone_1'], row['md_us_phone_2'], row['md_us_email'])
            writer.writerow(hashed_row)

def main():
    parser = argparse.ArgumentParser(description='Hash a dataset for privacy-preserving comparison, keeping pseudonyms clear.')
    parser.add_argument('--input-file', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output-file', type=str, required=True, help='Path for the output CSV file with hashes')
    args = parser.parse_args()
    hash_dataset(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
