from pinin.core import PincodeData  # Replace 'your_module' with your actual module name

# Create PincodeData instance
pincode_data = PincodeData()

# Example 1: Get all unique post office names in Tamil Nadu
unique_offices_tn = pincode_data.get_unique_offices_by_state("Tamil Nadu")

print("✅ Unique Post Offices in Tamil Nadu:")
if unique_offices_tn:
    for office in unique_offices_tn[:10]:  # Showing first 10 offices for demo
        print(f"- {office}")
else:
    print("No post offices found.")

# Example 2: Get all office types in Tamil Nadu
office_types_tn = pincode_data.get_office_types_by_state("Tamil Nadu")

print("\n✅ Office Types in Tamil Nadu:")
if office_types_tn:
    for office_type in office_types_tn:
        print(f"- {office_type}")
else:
    print("No office types found.")

    
# Create an instance of PincodeData
pincode_data = PincodeData()

# Example 1: Get all unique post offices in Tamil Nadu
unique_offices_tn = pincode_data.get_unique_offices_by_state("Tamil Nadu")
print("Unique Post Offices in Tamil Nadu:")
for office in unique_offices_tn:
    print(office)

# Example 2: Get office types available in Tamil Nadu
office_types_tn = pincode_data.get_office_types_by_state("Tamil Nadu")
print("\nOffice Types in Tamil Nadu:")
print(office_types_tn)

