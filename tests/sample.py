from pinin.core import PincodeData  # Adjust import based on your project structure

pincode_data = PincodeData()

# Suggest states & districts to find exact spelling from your data
print("Suggested States:", pincode_data.suggest_states("Tamil"))
print("Suggested Districts in Tamil Nadu:", pincode_data.suggest_districts("Tirup", state_name="Tamil Nadu"))

# Check all Taluks under 'Tiruppur' (this shows exact spelling in your dataset)
district_taluks = pincode_data.data[pincode_data.data['districtname'].str.upper() == "TIRUPPUR"]['taluk'].unique()
print("Taluks under Tiruppur District:", district_taluks)
