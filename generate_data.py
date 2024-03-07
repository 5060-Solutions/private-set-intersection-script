from faker import Faker
import csv

fake = Faker('en_US')

def generate_data(file_path, records=10, common_records=None):
    headers = ['pseudonym', 'u_account', 'u_firstname', 'u_name', 'u_zip', 'u_city', 'u_state', 'u_address', 'u_address2', 'md_country', 'md_us_phone_1', 'md_us_phone_2', 'md_companyname', 'md_us_email']
    
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for _ in range(records):
            writer.writerow([
                fake.user_name(), fake.bothify(text='???-###-###'), fake.first_name(), fake.last_name(),
                fake.zipcode(), fake.city(), fake.state_abbr(), fake.street_address(), "",
                fake.country(), fake.phone_number(), fake.phone_number(), fake.company(), fake.email()
            ])
        
        # Add common records if provided
        if common_records:
            for record in common_records:
                writer.writerow(record)

def main():
    common_records = [
        [fake.user_name(), fake.bothify(text='???-###-###'), fake.first_name(), fake.last_name(),
         fake.zipcode(), fake.city(), fake.state_abbr(), fake.street_address(), "",
         fake.country(), fake.phone_number(), fake.phone_number(), fake.company(), fake.email()]
        for _ in range(3)  # Number of common records
    ]

    generate_data('dataset1.csv', records=7, common_records=common_records)
    generate_data('dataset2.csv', records=7, common_records=common_records)

if __name__ == "__main__":
    main()
