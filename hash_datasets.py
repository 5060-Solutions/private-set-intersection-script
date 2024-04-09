import csv
import hashlib
import argparse

def hash_entry(row):
    columns = {
        'pseudonym': ['pseudonym'],
        'u_firstname': ['u_firstname', 'firstname', 'first_name'],
        'u_name': ['u_name', 'surname', 'last_name'],
        'u_city': ['u_city', 'city'],
        'u_state': ['u_state', 'state'],
        'md_us_phone_1': ['md_us_phone_1', 'phone1', 'phone_1'],
        'md_us_phone_2': ['md_us_phone_2', 'phone2', 'phone_2'],
        'md_us_email': ['md_us_email', 'email']
    }

    def get_column_value(column_variants):
        for variant in column_variants:
            if variant in row:
                return row[variant]
        return ''

    pseudonym = get_column_value(columns['pseudonym'])
    u_firstname = get_column_value(columns['u_firstname'])[0] if get_column_value(columns['u_firstname']) else ''
    u_name = get_column_value(columns['u_name'])
    u_city = get_column_value(columns['u_city'])
    u_state = get_column_value(columns['u_state'])
    md_us_phone_1 = get_column_value(columns['md_us_phone_1'])
    md_us_phone_2 = get_column_value(columns['md_us_phone_2'])
    email = get_column_value(columns['md_us_email'])

    phone_hash_1 = hashlib.sha256(md_us_phone_1.encode('utf-8')).hexdigest()
    phone_hash_2 = hashlib.sha256(md_us_phone_2.encode('utf-8')).hexdigest()
    personal_info_concat = f"{u_city}{u_state}{u_name}{u_firstname}"
    personal_info_hash = hashlib.sha256(personal_info_concat.encode('utf-8')).hexdigest()
    email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()

    return [pseudonym, phone_hash_1, phone_hash_2, personal_info_hash, email_hash]

def hash_dataset(input_file, output_file):
    with open(input_file, newline='') as csvfile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(outfile)
        writer.writerow(['Pseudonym', 'Phone Hash 1', 'Phone Hash 2', 'Personal Info Hash', 'Email Hash'])
        for row in reader:
            hashed_row = hash_entry(row)
            writer.writerow(hashed_row)

def main():
    parser = argparse.ArgumentParser(description='Hash a dataset for privacy-preserving comparison, keeping pseudonyms clear.')
    parser.add_argument('--input-file', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output-file', type=str, required=True, help='Path for the output CSV file with hashes')
    args = parser.parse_args()
    hash_dataset(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
