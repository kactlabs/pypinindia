from pinin.core import PincodeData, DataNotFoundError

# Initialize
pincode_data = PincodeData()

# ✅ Example 1: Typo in state name (Auto Suggestion)
try:
    pincodes = pincode_data.search_by_state("Taminadu")
    print("Pincodes:", pincodes)
except DataNotFoundError as e:
    print("Suggestion:", e)

# ✅ Example 2: Typo in district name (Auto Suggestion)
try:
    pincodes = pincode_data.search_by_district("Chennnai", state_name="Tamil Nadu")
    print("Pincodes:", pincodes)
except DataNotFoundError as e:
    print("Suggestion:", e)
