from pinin.core import PincodeData  # Replace with your actual module name

pincode_data = PincodeData()

# Test 1: Typo in state name - 'Tmilnadu' for 'Tamil Nadu'
print("Testing State Suggestion for 'Tmilnadu':")
suggested_states = pincode_data.suggest_states("Tmilnadu")
print("Suggestions:", suggested_states)
assert any(state.lower() == 'tamil nadu' for state in suggested_states), \
       "Test Failed: 'Tamil Nadu' not suggested."

# Test 2: Typo in district name - 'Bangaluru' for 'Bengaluru'
print("\nTesting District Suggestion for 'Bangaluru':")
suggested_districts = pincode_data.suggest_districts("Bangaluru")
print("Suggestions:", suggested_districts)
assert any(district.lower() == 'bengaluru' for district in suggested_districts), \
       "Test Failed: 'Bengaluru' not suggested."

# Test 3: District suggestion within a state (Optional Test)
print("\nTesting District Suggestion for 'Bangaluru' in 'Karnataka':")
suggested_districts_state = pincode_data.suggest_districts("Bangaluru", state_name="Karnataka")
print("Suggestions:", suggested_districts_state)
assert any(district.lower() == 'bengaluru' for district in suggested_districts_state), \
       "Test Failed: 'Bengaluru' not suggested within Karnataka."

print("\nAll tests passed successfully!")
