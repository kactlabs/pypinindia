from pinin.core import PincodeData  # Replace with your actual module name

# Initialize the PincodeData instance
pincode_data = PincodeData()

# Test 1: Suggest States
print("State suggestions for 'Tamilnadu':")
suggested_states = pincode_data.suggest_states("Tamilnadu")
print(suggested_states)

# Test 2: Suggest Districts (without state filter)
print("\nDistrict suggestions for 'Bangaluru':")
suggested_districts = pincode_data.suggest_districts("Bangaluru")
print(suggested_districts)

# Test 3: Suggest Districts (with state filter)
print("\nDistrict suggestions for 'Bangaluru' in 'Karnataka':")
suggested_districts_state = pincode_data.suggest_districts("Bangaluru", state_name="Karnataka")
print(suggested_districts_state)
