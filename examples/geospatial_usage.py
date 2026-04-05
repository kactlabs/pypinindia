#!/usr/bin/env python3
"""
Example usage of pypinindia geospatial features.

This script demonstrates how to use the new geospatial search capabilities
to find nearby pincodes and postal offices based on distance.
"""

from pypinindia import (
    get_nearby_pincodes, 
    get_nearest_pincodes, 
    get_pincode_coordinates,
    GeospatialData
)


def main():
    """Demonstrate geospatial search functionality."""
    
    print("=" * 60)
    print("pypinindia Geospatial Search Examples")
    print("=" * 60)
    
    # Example 1: Get coordinates for a pincode
    print("\n1. Getting coordinates for a pincode:")
    print("-" * 40)
    
    try:
        coords = get_pincode_coordinates("110001")
        print(f"Pincode: {coords['pincode']}")
        print(f"Coordinates: {coords['latitude']:.4f}, {coords['longitude']:.4f}")
        print(f"Location: {coords['district']}, {coords['state']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Find nearby pincodes
    print("\n2. Finding pincodes within 10km of 110001 (Delhi):")
    print("-" * 50)
    
    try:
        nearby = get_nearby_pincodes("110001", radius_km=10, limit=5)
        print(f"Found {len(nearby)} pincodes within 10km:")
        
        for i, pincode_info in enumerate(nearby, 1):
            print(f"{i:2d}. {pincode_info['pincode']} - {pincode_info['office_name']}")
            print(f"     {pincode_info['district']}, {pincode_info['state']}")
            print(f"     Distance: {pincode_info['distance_km']:.2f} km")
            print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Find nearest pincodes to coordinates
    print("\n3. Finding nearest pincodes to Mumbai coordinates:")
    print("-" * 50)
    
    try:
        # Mumbai coordinates
        mumbai_lat, mumbai_lon = 19.0760, 72.8777
        nearest = get_nearest_pincodes(mumbai_lat, mumbai_lon, limit=5)
        
        print(f"Nearest pincodes to ({mumbai_lat}, {mumbai_lon}):")
        
        for i, pincode_info in enumerate(nearest, 1):
            print(f"{i:2d}. {pincode_info['pincode']} - {pincode_info['office_name']}")
            print(f"     {pincode_info['district']}, {pincode_info['state']}")
            print(f"     Distance: {pincode_info['distance_km']:.2f} km")
            print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Calculate distance between cities
    print("\n4. Calculating distances between major cities:")
    print("-" * 50)
    
    cities = {
        'Delhi': (28.6139, 77.2090),
        'Mumbai': (19.0760, 72.8777),
        'Bangalore': (12.9716, 77.5946),
        'Chennai': (13.0827, 80.2707),
        'Kolkata': (22.5726, 88.3639)
    }
    
    delhi_coords = cities['Delhi']
    
    print("Distances from Delhi:")
    for city, coords in cities.items():
        if city != 'Delhi':
            distance = GeospatialData.haversine_distance(
                delhi_coords[0], delhi_coords[1],
                coords[0], coords[1]
            )
            print(f"  Delhi to {city}: {distance:.0f} km")
    
    # Example 5: Using GeospatialData class directly
    print("\n5. Using GeospatialData class for advanced operations:")
    print("-" * 55)
    
    try:
        geo_data = GeospatialData()
        
        # Find pincodes within a specific radius with custom parameters
        nearby_custom = geo_data.get_nearby_pincodes(
            "400001",  # Mumbai Fort area
            radius_km=15, 
            limit=3
        )
        
        print("Pincodes within 15km of Mumbai Fort (400001):")
        for pincode_info in nearby_custom:
            print(f"  {pincode_info['pincode']} - {pincode_info['office_name']}")
            print(f"    Distance: {pincode_info['distance_km']:.2f} km")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()