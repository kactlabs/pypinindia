# Example: Using the new get_unique_taluks method

from pinin.core import PincodeData  # replace with actual import

# Load Pincode Data
pincode_data = PincodeData()

# 1️⃣ Get all unique taluks
all_taluks = pincode_data.get_unique_taluks()
print("All Taluks:", all_taluks)

# 2️⃣ Get taluks filtered by state
tn_taluks = pincode_data.get_unique_taluks(state_name="Tamil Nadu")
print("Tamil Nadu Taluks:", tn_taluks)

# 3️⃣ Get taluks filtered by state and district
chennai_taluks = pincode_data.get_unique_taluks(state_name="Tamil Nadu", district_name="Chennai")
print("Chennai Taluks:", chennai_taluks)
