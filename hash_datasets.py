import csv
import hashlib
import argparse

def hash_entry(u_firstname, u_name, u_city, u_state, md_us_phone_1, md_us_phone_2):
    phone_hash_1 = hashlib.sha256(md_us_phone_1.encode('utf-8')).hexdigest()
    phone_hash_2 = hashlib.sha256(md_us_phone_2.encode('utf-8')).hexdigest()
    personal_info_concat = f"{u_city}{u_state}{u_name}{u_firstname[0]}"
    personal_info_hash = hashlib.sha256(personal_info_concat.encode('utf-8')).hexdigest()
    return phone_hash_1, phone_hash_2, personal_info_hash

def hash_dataset(file_path, output_file):
    with open(file_path, newline='') as csvfile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(outfile)
        for row in reader:
            hashes = hash_entry(row['u_firstname'], row['u_name'], row['u_city'], row['u_state'], row['md_us_phone_1'], row['md_us_phone_2'])
            writer.writerow(hashes)

def main():
    parser = argparse.ArgumentParser(description='Hash a dataset for privacy-preserving comparison.')
    parser.add_argument('--input-file', type=str, required=True, help='Path to the input CSV file to be hashed')
    parser.add_argument('--output-file', type=str, required=True, help='Path for the output CSV file containing the hashes')

    args = parser.parse_args()

    hash_dataset(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
