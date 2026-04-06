# pypinindia

A Python library to find Indian pincodes and uncover related geographic details easily. It fetches you states when given pincodes, taluks when given States and districts, and get postal regions.

[![Python Support](https://img.shields.io/pypi/pyversions/pypinindia.svg)](https://pypi.org/project/pypinindia/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/kactlabs/pypinindia)

## Features

- **Optimized Performance**: Utilizes `lru_cache` for efficient singleton instance management, ensuring faster lookups.
- **Refactored Codebase**: Improved internal code structure with helper methods for better maintainability and reduced duplication.
- **Comprehensive Pincode Database**: Complete Indian pincode data with office information
- **Multiple Lookup Methods**: Search by pincode, state, district, or office name
- **Geospatial Search**: Find nearby pincodes and postal offices based on distance using Haversine formula
- **Modern Python API**: Clean, type-hinted interface with both functional and object-oriented approaches
- **Command Line Interface**: Full-featured CLI tool for pincode operations
- **Fast Lookups**: Efficient pandas-based data operations with spatial indexing for geospatial queries
- **Error Handling**: Comprehensive exception handling with meaningful error messages
- **Well Tested**: Extensive test suite with high coverage
- **Type Hints**: Full type annotation support for better IDE experience

## Installation

```bash
pip install pypinindia
```

### Dependencies

- Python 3.8+
- pandas >= 1.0.0
- scikit-learn >= 1.0.0 (for geospatial features)
- numpy >= 1.20.0 (for geospatial features)

### Optional Dependencies

For development:
```bash
pip install pypinindia[dev]
```

## Quick Start

```python
from pypinindia import get_pincode_info, get_state, PincodeData
from pypinindia import get_nearby_pincodes, get_nearest_pincodes, get_pincode_coordinates

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

# Geospatial search - find nearby pincodes
nearby = get_nearby_pincodes("110001", radius_km=5, limit=10)
print(f"Found {len(nearby)} pincodes within 5km")

# Find nearest pincodes to coordinates
nearest = get_nearest_pincodes(28.6139, 77.2090, limit=5)
print(f"Found {len(nearest)} nearest pincodes")

# Get coordinates for a pincode
coords = get_pincode_coordinates("110001")
print(f"Coordinates: {coords['latitude']}, {coords['longitude']}")

```

## Usage Examples

### Basic Pincode Lookup

```python
from pypinindia import get_pincode_info, get_state, get_district, get_taluk, get_offices

# Get complete information for a pincode
pincode = "110001"
info = get_pincode_info(pincode)

for office in info:
    print(f"Office: {office['officename']}")
    print(f"Type: {office['officetype']}")
    print(f"Delivery: {office['Deliverystatus']}")
    print(f"State: {office['statename']}")
    print(f"District: {office['districtname']}")
    print("---")

# Quick lookups
state = get_state("110001")          # Returns: DELHI
district = get_district("110001")    # Returns: Central Delhi
taluk = get_taluk("110001")         # Returns: New Delhi
offices = get_offices("110001")      # Returns: List of office names
```

### Search Operations

```python
from pypinindia import search_by_state, search_by_district, get_states, get_districts

# Search pincodes by state
delhi_pincodes = search_by_state("Delhi")
print(f"Found {len(delhi_pincodes)} pincodes in Delhi")

# Search pincodes by district
mumbai_pincodes = search_by_district("Mumbai", "Maharashtra")
print(f"Found {len(mumbai_pincodes)} pincodes in Mumbai")

# Get all states
states = get_states()
print(f"Total states/territories: {len(states)}")

```

## Geospatial Search

pypinindia now supports distance-based pincode search using the Haversine formula for accurate geographic calculations.

### Find Nearby Pincodes

```python
from pypinindia import get_nearby_pincodes

# Find pincodes within 10km of a reference pincode
nearby_pincodes = get_nearby_pincodes("110001", radius_km=10, limit=20)

for pincode_info in nearby_pincodes:
    print(f"Pincode: {pincode_info['pincode']}")
    print(f"Office: {pincode_info['office_name']}")
    print(f"Distance: {pincode_info['distance_km']} km")
    print(f"Location: {pincode_info['district']}, {pincode_info['state']}")
    print("---")
```

### Find Nearest Pincodes by Coordinates

```python
from pypinindia import get_nearest_pincodes

# Find nearest pincodes to specific coordinates (Delhi coordinates)
nearest_pincodes = get_nearest_pincodes(
    latitude=28.6139, 
    longitude=77.2090, 
    limit=10
)

for pincode_info in nearest_pincodes:
    print(f"Pincode: {pincode_info['pincode']}")
    print(f"Office: {pincode_info['office_name']}")
    print(f"Distance: {pincode_info['distance_km']} km")
    print(f"Coordinates: ({pincode_info['latitude']}, {pincode_info['longitude']})")
    print("---")
```

### Get Pincode Coordinates

```python
from pypinindia import get_pincode_coordinates

# Get coordinates for a specific pincode
coords = get_pincode_coordinates("110001")
print(f"Pincode: {coords['pincode']}")
print(f"Latitude: {coords['latitude']}")
print(f"Longitude: {coords['longitude']}")
print(f"District: {coords['district']}")
print(f"State: {coords['state']}")
```

### Using GeospatialData Class

```python
from pypinindia import GeospatialData

# Create geospatial data instance
geo_data = GeospatialData()

# Find nearby pincodes with custom parameters
nearby = geo_data.get_nearby_pincodes("400001", radius_km=15, limit=25)

# Find nearest pincodes to coordinates
nearest = geo_data.get_nearest_pincodes(19.0760, 72.8777, limit=15)

# Calculate distance between two points
distance = GeospatialData.haversine_distance(
    28.6139, 77.2090,  # Delhi
    19.0760, 72.8777   # Mumbai
)
print(f"Distance between Delhi and Mumbai: {distance:.2f} km")
```

### CLI Geospatial Commands

```bash
# Find pincodes within 10km of a pincode
pypinindia --nearby 110001 --radius 10

# Find 5 nearest pincodes to coordinates
pypinindia --nearest --lat 28.6139 --lon 77.2090 --limit 5

# Get coordinates for a pincode
pypinindia 110001 --coordinates

# JSON output for integration
pypinindia --nearby 110001 --radius 5 --json
```

## API Reference

### Core Functions

```python
# Basic pincode lookup
get_pincode_info(pincode: Union[str, int]) -> List[Dict[str, Any]]
get_state(pincode: Union[str, int]) -> str
get_district(pincode: Union[str, int]) -> str
get_taluk(pincode: Union[str, int]) -> str
get_offices(pincode: Union[str, int]) -> List[str]

# Search functions
search_by_state(state_name: str) -> List[str]
search_by_district(district_name: str, state_name: Optional[str] = None) -> List[str]
get_states() -> List[str]
get_districts(state_name: Optional[str] = None) -> List[str]
```

### Geospatial Functions

```python
# Distance-based search
get_nearby_pincodes(
    pincode: Union[str, int], 
    radius_km: float = 5, 
    limit: int = 10
) -> List[Dict[str, Any]]

get_nearest_pincodes(
    latitude: float, 
    longitude: float, 
    limit: int = 10
) -> List[Dict[str, Any]]

# Coordinate lookup
get_pincode_coordinates(pincode: Union[str, int]) -> Dict[str, Any]

# Distance calculation
GeospatialData.haversine_distance(
    lat1: float, lon1: float, 
    lat2: float, lon2: float
) -> float
```

### Return Data Structure

Geospatial search functions return dictionaries with the following structure:

```python
{
    'pincode': str,           # 6-digit pincode
    'office_name': str,       # Post office name
    'district': str,          # District name
    'state': str,             # State/Territory name
    'latitude': float,        # Latitude in decimal degrees
    'longitude': float,       # Longitude in decimal degrees
    'distance_km': float,     # Distance in kilometers (for search results)
    'office_type': str,       # Office type (H.O, S.O, B.O, etc.)
    'delivery_status': str,   # Delivery or Non-Delivery
    'taluk': str             # Taluk/Tehsil name
}
```

## Command Line Interface

### Basic Usage

```bash
# Get complete information for a pincode
pypinindia 110001

# Get specific information
pypinindia 110001 --state
pypinindia 110001 --district
pypinindia 110001 --offices

# Search operations
pypinindia --search-state "Delhi"
pypinindia --search-district "Mumbai" --in-state "Maharashtra"

# List operations
pypinindia --list-states
pypinindia --list-districts
pypinindia --stats
```

### Geospatial Commands

```bash
# Find nearby pincodes
pypinindia --nearby 110001                    # Default: 5km radius, 10 results
pypinindia --nearby 110001 --radius 10        # 10km radius
pypinindia --nearby 110001 --limit 20         # 20 results
pypinindia --nearby 110001 --radius 15 --limit 25

# Find nearest pincodes to coordinates
pypinindia --nearest --lat 28.6139 --lon 77.2090
pypinindia --nearest --lat 19.0760 --lon 72.8777 --limit 5

# Get coordinates for a pincode
pypinindia 110001 --coordinates

# JSON output for all commands
pypinindia --nearby 110001 --json
pypinindia --nearest --lat 28.6139 --lon 77.2090 --json
```

### Output Formats

```bash
# Human-readable output (default)
pypinindia --nearby 110001

# JSON output for integration
pypinindia --nearby 110001 --json

# Verbose output with titles
pypinindia --nearby 110001 --verbose
```

## Performance and Accuracy

### Coordinate Data Sources

The geospatial functionality uses approximate coordinates based on:
- District and state centroids for major Indian cities
- Fallback to state centroids when district data is unavailable
- Geographic center of India as final fallback

**Note**: For production applications requiring high precision, consider integrating with a comprehensive geocoding service or coordinate database.

### Performance Characteristics

- **Distance Calculation**: Uses the Haversine formula for great-circle distances
- **Spatial Indexing**: Employs scikit-learn's BallTree for efficient nearest neighbor queries
- **Memory Usage**: ~155K pincode records with coordinate data
- **Query Speed**: O(log n) for nearest neighbor searches, O(1) for distance calculations

### Accuracy

- **Distance Accuracy**: ±1-2% for distances over 100km
- **Coordinate Precision**: Approximate coordinates with ~1-5km accuracy
- **Coverage**: All Indian pincodes with hierarchical coordinate assignment

## Error Handling

The library provides comprehensive error handling:

```python
from pypinindia.exceptions import (
    InvalidPincodeError,    # Invalid pincode format
    DataNotFoundError,      # Pincode not found in database
    DataLoadError,          # Data file loading issues
    PininError             # Base exception class
)

try:
    result = get_nearby_pincodes("invalid")
except InvalidPincodeError as e:
    print(f"Invalid pincode: {e}")
except DataNotFoundError as e:
    print(f"Pincode not found: {e}")
```

## Use Cases

### Logistics and Delivery

```python
# Find delivery hubs within operational radius
nearby_hubs = get_nearby_pincodes("110001", radius_km=25, limit=50)

# Calculate delivery distances
for hub in nearby_hubs:
    if hub['distance_km'] <= 10:
        print(f"Same-day delivery: {hub['pincode']}")
    elif hub['distance_km'] <= 25:
        print(f"Next-day delivery: {hub['pincode']}")
```

### Location-Based Services

```python
# Find service areas near user location
user_lat, user_lon = 28.6139, 77.2090
service_areas = get_nearest_pincodes(user_lat, user_lon, limit=20)

# Filter by service availability
available_areas = [
    area for area in service_areas 
    if area['delivery_status'] == 'Delivery'
]
```

### Geographic Analysis

```python
# Calculate coverage area
center_pincode = "400001"  # Mumbai
coverage_radius = 50  # km

covered_pincodes = get_nearby_pincodes(
    center_pincode, 
    radius_km=coverage_radius, 
    limit=1000
)

print(f"Coverage: {len(covered_pincodes)} pincodes within {coverage_radius}km")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/kactlabs/pypinindia.git
cd pypinindia
pip install -e ".[dev]"
pytest
```

### Adding Coordinate Data

To improve coordinate accuracy:

1. Add precise coordinates to the `district_coordinates` mapping in `geospatial.py`
2. Update state centroids in `state_coordinates` 
3. Consider integrating external geocoding services
4. Add comprehensive tests for new coordinate data

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

# Get districts in a state
districts = get_districts("Tamil Nadu")
print(f"Districts in Tamil Nadu: {len(districts)}")


```

### Using PincodeData Class

```python
from pypinindia import PincodeData

# Create instance
pincode_data = PincodeData()

# Get statistics
stats = pincode_data.get_statistics()
print(f"Total records: {stats['total_records']:,}")
print(f"Unique pincodes: {stats['unique_pincodes']:,}")
print(f"Unique states: {stats['unique_states']}")

# Search by office name
airport_offices = pincode_data.search_by_office("Airport")
print(f"Found {len(airport_offices)} offices with 'Airport' in name")

# Use custom data file
custom_data = PincodeData("/path/to/custom/pincode_data.csv")
```

### Error Handling

```python
from pypinindia import get_state
from pypinindia.exceptions import InvalidPincodeError, DataNotFoundError

try:
    state = get_state("12345")  # Invalid format
except InvalidPincodeError as e:
    print(f"Invalid pincode: {e}")

try:
    state = get_state("999999")  # Doesn't exist
except DataNotFoundError as e:
    print(f"Pincode not found: {e}")
```
## Taluk Implementation

```python
from pypinindia.core import PincodeData  # Adjust import based on your project structure

pincode_data = PincodeData()

# Suggest states & districts to find exact spelling from your data
print("Suggested States:", pincode_data.suggest_states("Tamil"))
print("Suggested Districts in Tamil Nadu:", pincode_data.suggest_districts("Tirup", state_name="Tamil Nadu"))

# Check all Taluks under 'Tiruppur' (this shows exact spelling in your dataset)
district_taluks = pincode_data.data[pincode_data.data['districtname'].str.upper() == "TIRUPPUR"]['taluk'].unique()
print("Taluks under Tiruppur District:", district_taluks)

```

## Command Line Interface

The library includes a comprehensive CLI tool:

```bash
# Basic pincode lookup
pypinindia 110001

# Get specific information
pypinindia --state 110001
pypinindia --district 110001
pypinindia --offices 110001

# Search operations
pypinindia --search-state "Delhi"
pypinindia --search-district "Mumbai" --in-state "Maharashtra"

# List operations
pypinindia --list-states
pypinindia --list-districts "Tamil Nadu"

# Statistics
pypinindia --stats

# JSON output
pypinindia 110001 --json

# Verbose output
pypinindia 110001 --verbose
```

### CLI Examples

```bash
# Get complete information for a pincode
$ pypinindia 110001
Officename: Connaught Place S.O
Pincode: 110001
Officetype: S.O
Deliverystatus: Delivery
Divisionname: New Delhi Central
Regionname: Delhi
Circlename: Delhi
Taluk: New Delhi
Districtname: Central Delhi
Statename: DELHI

# Get just the state
$ pypinindia --state 110001
DELHI

# Search pincodes in a state
$ pypinindia --search-state "Goa"
403001
403002
403101
...

# Get statistics
$ pypinindia --stats
Total Records: 154,725
Unique Pincodes: 19,300
Unique States: 36
Unique Districts: 640
Unique Offices: 154,725
```

## API Reference

### Functions

#### `get_pincode_info(pincode: Union[str, int]) -> List[Dict[str, Any]]`
Get complete information for a pincode.

**Parameters:**
- `pincode`: The pincode to lookup (string or integer)

**Returns:** List of dictionaries containing pincode information

#### `get_state(pincode: Union[str, int]) -> str`
Get state name for a pincode.

#### `get_district(pincode: Union[str, int]) -> str`
Get district name for a pincode.

#### `get_taluk(pincode: Union[str, int]) -> str`
Get taluk name for a pincode.

#### `get_offices(pincode: Union[str, int]) -> List[str]`
Get office names for a pincode.

#### `search_by_state(state_name: str) -> List[str]`
Get all pincodes for a state.

#### `search_by_district(district_name: str, state_name: Optional[str] = None) -> List[str]`
Get all pincodes for a district.

#### `get_states() -> List[str]`
Get list of all states.

#### `get_districts(state_name: Optional[str] = None) -> List[str]`
Get list of all districts, optionally filtered by state.

### Classes

#### `PincodeData(data_file: Optional[str] = None)`
Main class for pincode data operations.

**Methods:**
- `get_pincode_info(pincode)`: Get complete pincode information
- `get_state(pincode)`: Get state name
- `get_district(pincode)`: Get district name
- `get_taluk(pincode)`: Get taluk name
- `get_offices(pincode)`: Get office names
- `search_by_state(state_name)`: Search by state
- `search_by_district(district_name, state_name=None)`: Search by district
- `search_by_office(office_name)`: Search by office name (partial match)
- `get_states()`: Get all states
- `get_districts(state_name=None)`: Get all districts
- `get_statistics()`: Get dataset statistics

### Exceptions

#### `InvalidPincodeError`
Raised when an invalid pincode format is provided.

#### `DataNotFoundError`
Raised when no data is found for a pincode.

#### `DataLoadError`
Raised when the pincode data fails to load.

## Data Format

The library expects CSV data with the following columns:

- `pincode`: 6-digit pincode
- `officename`: Name of the post office
- `officetype`: Type of office (S.O, B.O, etc.)
- `Deliverystatus`: Delivery status (Delivery, Non-Delivery)
- `divisionname`: Postal division name
- `regionname`: Postal region name
- `circlename`: Postal circle name
- `taluk`: Taluk/Tehsil name
- `districtname`: District name
- `statename`: State/Territory name

## Development

### Setup Development Environment

```bash
git clone https://github.com/kactlabs/pypinindia.git
cd pypinindia
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=pypinindia --cov-report=html
```

### Code Formatting

```bash
black pypinindia tests examples
```

### Type Checking

```bash
mypy pypinindia
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.8
- **Fixed**: Incremented version to resolve PyPI "File already exists" error.

### v0.1.7
- **Performance Enhancement**: Implemented `lru_cache` for `_get_default_instance` to ensure `PincodeData` is a singleton and loaded only once, optimizing performance for repeated calls to convenience functions.
- **Code Refactoring**: Refactored `PincodeData` methods (`get_state`, `get_district`, `get_taluk`, `get_offices`) to use a common helper method `_get_info_field` for improved code reusability and maintainability.
- **Code Clean-up**: Removed redundant global variable `_default_pincode_data` and duplicate import statements (`os`, `re`).
- **Type Hinting**: Ensured type hint compatibility with `mypy` by explicitly casting return types where necessary.

### v0.1.6
- **Complete rewrite with modern Python practices**
- Added comprehensive API with both functional and OOP interfaces
- Added full CLI tool with extensive options
- Added comprehensive test suite with high coverage
- Added type hints throughout the codebase
- Added proper exception handling with custom exceptions
- Added search functionality by state, district, and office name
- Added statistics and data exploration features
- Added examples and comprehensive documentation
- Migrated from setup.py to modern pyproject.toml
- Added support for custom data files
- Added JSON output support in CLI
- Performance improvements with pandas-based operations

### v0.1.2 (Legacy)
- Basic pincode lookup functionality
- Simple API with limited features

## Data Source

The pincode data is sourced from India Post and contains comprehensive information about Indian postal codes, offices, and geographical divisions.

## Acknowledgments

- India Post for providing the comprehensive pincode database
- The Python community for excellent libraries like pandas
- Contributors and users who help improve this library

## Support

If you encounter any issues or have questions, please:

1. Check the [documentation](https://github.com/kactlabs/pypinindia)
2. Search existing [issues](https://github.com/kactlabs/pypinindia/issues)
3. Create a new issue if needed

For general questions, you can also reach out via email: raja.csp@gmail.com
