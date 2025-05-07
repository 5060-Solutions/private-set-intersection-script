import argparse
import csv
import hashlib
import re
from typing import Any, Dict, List, Optional

import phonenumbers

debug_mode = False
phone_warnings = {
    "md_us_phone_1_blank": 0,
    "md_us_phone_2_blank": 0,
    "md_us_phone_3_blank": 0,
    "md_us_phone_1_invalid": 0,
    "md_us_phone_2_invalid": 0,
    "md_us_phone_3_invalid": 0,
    "md_us_phone_1_success": 0,
    "md_us_phone_2_success": 0,
    "md_us_phone_3_success": 0,
}


def debug_print(message: str) -> None:
    """Print debug messages when debug mode is enabled."""
    if debug_mode:
        print(message)


def standardize_phone_number(phone: str, pseudonym: str, phone_label: str) -> tuple[str, Optional[str]]:
    """
    Standardize phone numbers to E.164 format using libphonenumber.

    Args:
        phone: The input phone number string
        pseudonym: The pseudonym for error reporting
        phone_label: Label for the phone field (md_us_phone_1, md_us_phone_2, etc.)

    Returns:
        A tuple containing:
            - Standardized phone number in E.164 format (or empty string if invalid/blank).
            - A string describing the failure reason (or None if successful).
    """
    if phone is None or phone.strip() == "":
        debug_print(f"Warning: Blank phone number for pseudonym '{pseudonym}', field '{phone_label}'")
        phone_warnings[f"{phone_label}_blank"] += 1
        return "", "Blank phone number"

    try:
        parsed_phone = phonenumbers.parse(phone, "US")

        if phonenumbers.is_valid_number(parsed_phone):
            formatted_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
            debug_print(
                f"Formatted phone number for '{pseudonym}': Original '{phone}' => Formatted '{formatted_phone}'"
            )
            phone_warnings[f"{phone_label}_success"] += 1
            return formatted_phone, None
        else:
            reason = "Invalid phone number"
            if not phonenumbers.is_possible_number(parsed_phone):
                reason = "Not a possible number"
            elif phonenumbers.number_type(parsed_phone) == phonenumbers.PhoneNumberType.UNKNOWN:
                reason = "Unknown number type"

            debug_print(f"Warning: Invalid phone number '{phone}' for pseudonym '{pseudonym}': {reason}")
            phone_warnings[f"{phone_label}_invalid"] += 1
            return "", reason

    except phonenumbers.NumberParseException as e:
        phone_warnings[f"{phone_label}_invalid"] += 1
        error_message = f"Failed to parse phone number: {e}"
        debug_print(f"Warning: {error_message} for '{phone}' pseudonym '{pseudonym}'")
        return "", error_message


state_province_codes = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "Ontario": "ON",
    "Quebec": "QC",
    "Nova Scotia": "NS",
    "New Brunswick": "NB",
    "Manitoba": "MB",
    "British Columbia": "BC",
    "Prince Edward Island": "PE",
    "Saskatchewan": "SK",
    "Alberta": "AB",
    "Newfoundland and Labrador": "NL",
}


def normalize_state_province(name: str) -> str:
    """Normalize state/province names to standard two-letter codes."""
    return state_province_codes.get(name.title(), name)


def normalize_address(address: str) -> str:
    """
    Normalize an address by standardizing format and removing apartment/unit numbers.

    Args:
        address: The input address string

    Returns:
        Normalized address string
    """
    if not address:
        return ""
    address = address.lower().strip()
    address = re.sub(r"^[,.\s]+|[,.\s]+$", "", address)
    address = re.sub(r"\b(?:apartment|apt|suite|ste|unit|fl|floor|#)\s*[\w-]+\b", "", address)
    substitutions = {
        "street": "st",
        "avenue": "ave",
        "road": "rd",
        "drive": "dr",
        "place": "pl",
        "lane": "ln",
        "highway": "hwy",
        "court": "ct",
        "square": "sq",
        "loop": "lp",
        "trail": "trl",
        "parkway": "pkwy",
        "commons": "cmns",
        "north": "n",
        "south": "s",
        "east": "e",
        "west": "w",
        "boulevard": "blvd",
        "circle": "cir",
        "terrace": "ter",
    }
    for k, v in substitutions.items():
        address = re.sub(rf"\b{k}\b\.?", v, address)
    address = re.sub(r"[^\w\s]", "", address)
    address = re.sub(r"\s+", " ", address).strip()
    return address


def hash_entry(row: Dict[str, str]) -> tuple[Optional[List[str]], List[Dict[str, Any]]]:
    """
    Process a row from the input file and generate hashed values.
    It also collects details of any phone numbers that failed standardization.

    Args:
        row: Dictionary containing the row data

    Returns:
        A tuple containing:
            - List of values for output (hashed_row) or None if the row should be skipped.
            - A list of dictionaries, where each dictionary contains details of a bad phone record.
    """
    columns = {
        "pseudonym": ["Panelistid", "pseudonym", "uniqueid", "index"],
        "u_firstname": ["FirstName", "u_firstname", "firstname", "first_name"],
        "u_name": ["LastName", "u_name", "surname", "last_name"],
        "u_city": ["City", "u_city", "city"],
        "u_state": ["State", "u_state", "state"],
        "md_us_phone_1": ["Phone 1", "md_us_phone_1", "phone1", "phone_1", "md_us_phone_1_rec"],
        "md_us_phone_2": ["Phone 2", "md_us_phone_2", "phone2", "phone_2", "md_us_phone_2_rec"],
        "md_us_phone_3": ["Phone 3", "md_us_phone_3", "phone3", "phone_3", "md_us_phone_3_rec"],
        "md_us_email": ["Email", "md_us_email", "email"],
    }

    bad_phone_records = []

    def get_column_value(column_variants: List[str]) -> str:
        """Get the value from the first matching column name in the row."""
        for variant in column_variants:
            if variant in row:
                return row[variant].strip().lower()
        return ""

    pseudonym = get_column_value(columns["pseudonym"])
    if not pseudonym:
        return None, []

    u_firstname = get_column_value(columns["u_firstname"])[0] if get_column_value(columns["u_firstname"]) else ""
    u_name = get_column_value(columns["u_name"])
    u_city = normalize_address(get_column_value(columns["u_city"]))
    u_state = normalize_state_province(get_column_value(columns["u_state"]))

    phone_fields_to_process = [
        ("md_us_phone_1", columns["md_us_phone_1"]),
        ("md_us_phone_2", columns["md_us_phone_2"]),
        ("md_us_phone_3", columns["md_us_phone_3"]),
    ]

    processed_phones = {}
    for phone_label, column_variants in phone_fields_to_process:
        original_phone_value = get_column_value(column_variants)
        std_phone, reason = standardize_phone_number(original_phone_value, pseudonym, phone_label)
        processed_phones[phone_label] = std_phone
        if reason and reason != "Blank phone number":
            bad_record_detail = {
                "Pseudonym": pseudonym,
                "OriginalPhoneInput": original_phone_value,
                "PhoneFieldLabel": phone_label,
                "ReasonForFailure": reason,
            }
            # Add all original row data to the bad record for full context
            bad_record_detail.update(row)
            bad_phone_records.append(bad_record_detail)

    email = get_column_value(columns["md_us_email"])
    personal_info_concat = f"{u_city}{u_state}{u_name}{u_firstname}"

    hashed_row = [pseudonym]
    for value in [
        processed_phones["md_us_phone_1"],
        processed_phones["md_us_phone_2"],
        processed_phones["md_us_phone_3"],
        personal_info_concat,
        email,
    ]:
        if value:
            hashed_row.append(hashlib.sha256(value.encode("utf-8")).hexdigest())
        else:
            hashed_row.append("")

    return hashed_row, bad_phone_records


def hash_dataset(input_file: str, output_file: str, bad_records_file: Optional[str] = None) -> None:
    """
    Process the input file and generate a hashed output file.
    Optionally, write records with bad phone numbers to a separate CSV file.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
        bad_records_file: Optional path for a CSV file to store records with bad phone numbers
    """
    bad_records_writer = None
    bad_records_csvfile = None
    # Keep track of original fieldnames for the bad records file
    original_fieldnames: List[str] = []

    try:
        with open(input_file, newline="", encoding="latin-1") as csvfile, open(
            output_file, "w", newline="", encoding="utf-8"
        ) as outfile:
            reader = csv.DictReader(csvfile)
            writer = csv.writer(outfile)

            original_fieldnames = list(reader.fieldnames) if reader.fieldnames else []

            if bad_records_file and original_fieldnames:
                bad_records_csvfile = open(bad_records_file, "w", newline="", encoding="utf-8")
                bad_records_writer = csv.writer(bad_records_csvfile)
                header_row_bad_records = [
                    "Pseudonym",
                    "OriginalPhoneInput",
                    "PhoneFieldLabel",
                    "ReasonForFailure",
                ] + original_fieldnames
                bad_records_writer.writerow(header_row_bad_records)

            writer.writerow(
                [
                    "Pseudonym",
                    "Phone Hash 1",
                    "Phone Hash 2",
                    "Phone Hash 3",
                    "Personal Info Hash",
                    "Email Hash",
                ]
            )
            total_rows, skipped_rows, hashed_rows, bad_phone_entries_written = 0, 0, 0, 0
            for row in reader:
                total_rows += 1
                hashed_row, bad_phone_details_list = hash_entry(row)
                if hashed_row is None:
                    skipped_rows += 1
                    continue
                writer.writerow(hashed_row)
                hashed_rows += 1

                if bad_records_writer and bad_phone_details_list:
                    for bad_detail in bad_phone_details_list:
                        # Construct the row for the bad records file carefully based on header_row_bad_records
                        # The first few fields are from bad_detail, the rest are from the original row
                        # (which is already in bad_detail)
                        record_to_write = [
                            bad_detail.get("Pseudonym", ""),
                            bad_detail.get("OriginalPhoneInput", ""),
                            bad_detail.get("PhoneFieldLabel", ""),
                            bad_detail.get("ReasonForFailure", ""),
                        ]
                        for fieldname in original_fieldnames:
                            record_to_write.append(bad_detail.get(fieldname, ""))
                        bad_records_writer.writerow(record_to_write)
                        bad_phone_entries_written += 1

            print(f"Input file: {input_file}")
            print(f"Output file: {output_file}")
            if bad_records_file:
                print(f"Bad records file: {bad_records_file}")
                print(f"Total bad phone entries written: {bad_phone_entries_written}")
            print(f"Total rows processed: {total_rows}")
            print(f"Rows hashed and written to output: {hashed_rows}")
            print(f"Rows skipped due to blank pseudonym: {skipped_rows}")
            print("Phone number processing summary:")
            for key, count in phone_warnings.items():
                print(f"- {key.replace('_', ' ').title()}: {count}")
    finally:
        if bad_records_csvfile:
            bad_records_csvfile.close()


def main():
    """Main entry point for the script."""
    global debug_mode
    parser = argparse.ArgumentParser(
        description="Hash a dataset for privacy-preserving comparison, keeping pseudonyms clear."
    )
    parser.add_argument("--input-file", type=str, required=True, help="Path to the input CSV file")
    parser.add_argument("--output-file", type=str, required=True, help="Path for the output CSV file with hashes")
    parser.add_argument(
        "--bad-records-file",
        type=str,
        required=False,
        help="Optional path for CSV file to store records with bad phone numbers",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    debug_mode = args.debug
    hash_dataset(args.input_file, args.output_file, args.bad_records_file)


if __name__ == "__main__":
    main()
