from pinin import get_pincode_info, get_state, PincodeData

# Quick pincode lookup
info = get_pincode_info("110001")
print(f"Found {len(info)} offices for pincode 110001")

# Get specific information
state = get_state("110001")
print(f"State: {state}")

# Using PincodeData class
pincode_data = PincodeData()
district = pincode_data.get_district("110001")
print(f"District: {district}")