from pinin.core import PincodeData  # Replace 'your_module' with your actual module name

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
