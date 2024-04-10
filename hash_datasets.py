import csv
import hashlib
import argparse
import phonenumbers
import re

debug_mode = False
phone_warnings = {
    'md_us_phone_1_blank': 0,
    'md_us_phone_2_blank': 0,
    'md_us_phone_1_invalid': 0,
    'md_us_phone_2_invalid': 0,
    'md_us_phone_1_success': 0,
    'md_us_phone_2_success': 0
}

def debug_print(message):
    if debug_mode:
        print(message)

def standardize_phone_number(phone, pseudonym, phone_label):
    if phone is None or phone.strip() == "":
        debug_print(f"Warning: Encountered a None or blank phone number for pseudonym '{pseudonym}', treating as empty string.")
        phone_warnings[f'{phone_label}_blank'] += 1
        return ""
    try:
        parsed_phone = phonenumbers.parse(phone, "US")
        if phonenumbers.is_valid_number(parsed_phone):
            formatted_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
            debug_print(f"Formatted phone number for '{pseudonym}': Original '{phone}' => Formatted '{formatted_phone}'")
            phone_warnings[f'{phone_label}_success'] += 1
            return formatted_phone
    except phonenumbers.NumberParseException as e:
        phone_warnings[f'{phone_label}_invalid'] += 1
        debug_print(f"Warning: Failed to parse phone number '{phone}' for pseudonym '{pseudonym}': {e}")
    return ""

state_province_codes = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "Ontario": "ON", "Quebec": "QC", "Nova Scotia": "NS", "New Brunswick": "NB",
    "Manitoba": "MB", "British Columbia": "BC", "Prince Edward Island": "PE", 
    "Saskatchewan": "SK", "Alberta": "AB", "Newfoundland and Labrador": "NL",
}

def normalize_state_province(name):
    return state_province_codes.get(name.title(), name)

def normalize_address(address):
    if not address:
        return ""
    address = address.lower().strip()
    address = re.sub(r'^[,.\s]+|[,.\s]+$', '', address)
    address = re.sub(r'\b(?:apartment|apt|suite|ste|unit|fl|floor|#)\s*[\w-]+\b', '', address)
    substitutions = {
        'street': 'st', 'avenue': 'ave', 'road': 'rd', 'drive': 'dr', 'place': 'pl', 
        'lane': 'ln', 'highway': 'hwy', 'court': 'ct', 'square': 'sq', 'loop': 'lp',
        'trail': 'trl', 'parkway': 'pkwy', 'commons': 'cmns', 'north': 'n', 'south': 's',
        'east': 'e', 'west': 'w', 'boulevard': 'blvd', 'circle': 'cir', 'terrace': 'ter'
    }
    for k, v in substitutions.items():
        address = re.sub(rf'\b{k}\b\.?', v, address)
    address = re.sub(r'[^\w\s]', '', address)
    address = re.sub(r'\s+', ' ', address).strip()
    return address

def hash_entry(row):
    columns = {
        'pseudonym': ['pseudonym', 'uniqueid', 'index'],
        'u_firstname': ['u_firstname', 'firstname', 'first_name'],
        'u_name': ['u_name', 'surname', 'last_name'],
        'u_city': ['u_city', 'city'],
        'u_state': ['u_state', 'state'],
        'md_us_phone_1': ['md_us_phone_1', 'phone1', 'phone_1', 'md_us_phone_1_rec'],
        'md_us_phone_2': ['md_us_phone_2', 'phone2', 'phone_2', 'md_us_phone_2_rec'],
        'md_us_email': ['md_us_email', 'email']
    }

    def get_column_value(column_variants):
        for variant in column_variants:
            if variant in row:
                return row[variant].strip().lower()
        return ''

    pseudonym = get_column_value(columns['pseudonym'])
    if not pseudonym:
        return None

    u_firstname = get_column_value(columns['u_firstname'])[0] if get_column_value(columns['u_firstname']) else ''
    u_name = get_column_value(columns['u_name'])
    u_city = normalize_address(get_column_value(columns['u_city']))
    u_state = normalize_state_province(get_column_value(columns['u_state']))
    md_us_phone_1 = standardize_phone_number(get_column_value(columns['md_us_phone_1']), pseudonym, 'md_us_phone_1')
    md_us_phone_2 = standardize_phone_number(get_column_value(columns['md_us_phone_2']), pseudonym, 'md_us_phone_2')
    email = get_column_value(columns['md_us_email'])

    personal_info_concat = f"{u_city}{u_state}{u_name}{u_firstname}"

    hashed_row = [pseudonym]
    for value in [md_us_phone_1, md_us_phone_2, personal_info_concat, email]:
        if value:
            hashed_row.append(hashlib.sha256(value.encode('utf-8')).hexdigest())
        else:
            hashed_row.append("")

    return hashed_row

def hash_dataset(input_file, output_file):
    global invalid_phone_warnings
    with open(input_file, newline='', encoding='utf-8-sig') as csvfile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(outfile)
        writer.writerow(['Pseudonym', 'Phone Hash 1', 'Phone Hash 2', 'Personal Info Hash', 'Email Hash'])
        total_rows, skipped_rows, hashed_rows = 0, 0, 0
        for row in reader:
            total_rows += 1
            hashed_row = hash_entry(row)
            if hashed_row is None:
                skipped_rows += 1
                continue
            writer.writerow(hashed_row)
            hashed_rows += 1
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Total rows processed: {total_rows}")
        print(f"Rows hashed and written to output: {hashed_rows}")
        print(f"Rows skipped due to blank pseudonym: {skipped_rows}")
        print("Phone number processing summary:")
        for key, count in phone_warnings.items():
            print(f"- {key.replace('_', ' ').title()}: {count}")

def main():
    global debug_mode
    parser = argparse.ArgumentParser(description='Hash a dataset for privacy-preserving comparison, keeping pseudonyms clear.')
    parser.add_argument('--input-file', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output-file', type=str, required=True, help='Path for the output CSV file with hashes')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    debug_mode = args.debug

    global invalid_phone_warnings
    invalid_phone_warnings = 0

    hash_dataset(args.input_file, args.output_file)

if __name__ == "__main__":
    main()