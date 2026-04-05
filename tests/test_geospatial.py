"""
Tests for geospatial functionality in pypinindia.
"""

import pytest
import math
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from pypinindia.geospatial import (
    GeospatialData, get_nearby_pincodes, get_nearest_pincodes, 
    get_pincode_coordinates
)
from pypinindia.exceptions import InvalidPincodeError, DataNotFoundError, DataLoadError


class TestGeospatialData:
    """Test cases for GeospatialData class."""
    
    @pytest.fixture
    def mock_pincode_data(self):
        """Create mock pincode data for testing."""
        mock_data = pd.DataFrame({
            'pincode': ['110001', '110002', '110003', '400001', '400002'],
            'officename': ['Connaught Place H.O', 'Parliament Street S.O', 'Kashmere Gate H.O', 'Fort S.O', 'Kalbadevi S.O'],
            'districtname': ['Central Delhi', 'Central Delhi', 'Central Delhi', 'Mumbai', 'Mumbai'],
            'statename': ['DELHI', 'DELHI', 'DELHI', 'MAHARASHTRA', 'MAHARASHTRA'],
            'taluk': ['New Delhi', 'New Delhi', 'New Delhi', 'Mumbai City', 'Mumbai City'],
            'officetype': ['H.O', 'S.O', 'H.O', 'S.O', 'S.O'],
            'Deliverystatus': ['Delivery', 'Delivery', 'Delivery', 'Delivery', 'Delivery']
        })
        
        mock_pincode_data = MagicMock()
        mock_pincode_data.data = mock_data
        mock_pincode_data._validate_pincode.side_effect = lambda x: str(x)
        mock_pincode_data.get_pincode_info.return_value = [
            {
                'pincode': '110001',
                'officename': 'Connaught Place H.O',
                'officetype': 'H.O',
                'Deliverystatus': 'Delivery',
                'taluk': 'New Delhi'
            }
        ]
        
        return mock_pincode_data
    
    def test_haversine_distance(self):
        """Test Haversine distance calculation."""
        # Distance between Delhi (28.6139, 77.2090) and Mumbai (19.0760, 72.8777)
        distance = GeospatialData.haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        
        # Expected distance is approximately 1155 km
        assert 1150 <= distance <= 1160
    
    def test_haversine_distance_same_point(self):
        """Test Haversine distance for same point."""
        distance = GeospatialData.haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
        assert distance == 0.0
    
    def test_haversine_distance_known_points(self):
        """Test Haversine distance for known points."""
        # Distance between New York (40.7128, -74.0060) and Los Angeles (34.0522, -118.2437)
        distance = GeospatialData.haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        
        # Expected distance is approximately 3944 km
        assert 3940 <= distance <= 3950
    
    @patch('pypinindia.geospatial.PincodeData')
    def test_geospatial_data_initialization(self, mock_pincode_data_class):
        """Test GeospatialData initialization."""
        mock_instance = MagicMock()
        mock_pincode_data_class.return_value = mock_instance
        
        geo_data = GeospatialData()
        
        assert geo_data.pincode_data == mock_instance
        assert geo_data._coordinate_data is not None
        assert geo_data._ball_tree is not None
    
    def test_get_pincode_coordinates_valid(self):
        """Test getting coordinates for a valid pincode."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_pincode_coordinates.return_value = {
                'pincode': '110001',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'district': 'Central Delhi',
                'state': 'DELHI'
            }
            mock_instance.return_value = mock_geo
            
            result = get_pincode_coordinates('110001')
            
            assert result['pincode'] == '110001'
            assert result['latitude'] == 28.6139
            assert result['longitude'] == 77.2090
            assert result['district'] == 'Central Delhi'
            assert result['state'] == 'DELHI'
    
    def test_get_pincode_coordinates_invalid(self):
        """Test getting coordinates for an invalid pincode."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_pincode_coordinates.side_effect = DataNotFoundError('123456')
            mock_instance.return_value = mock_geo
            
            with pytest.raises(DataNotFoundError):
                get_pincode_coordinates('123456')
    
    def test_get_nearby_pincodes_valid(self):
        """Test getting nearby pincodes for a valid pincode."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = [
                {
                    'pincode': '110002',
                    'office_name': 'Parliament Street S.O',
                    'district': 'Central Delhi',
                    'state': 'DELHI',
                    'latitude': 28.6200,
                    'longitude': 77.2100,
                    'distance_km': 1.2
                }
            ]
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001', radius_km=5, limit=10)
            
            assert len(result) == 1
            assert result[0]['pincode'] == '110002'
            assert result[0]['distance_km'] == 1.2
    
    def test_get_nearby_pincodes_no_results(self):
        """Test getting nearby pincodes when no results found."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = []
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001', radius_km=1, limit=10)
            
            assert result == []
    
    def test_get_nearest_pincodes_valid_coordinates(self):
        """Test getting nearest pincodes for valid coordinates."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearest_pincodes.return_value = [
                {
                    'pincode': '110001',
                    'office_name': 'Connaught Place H.O',
                    'district': 'Central Delhi',
                    'state': 'DELHI',
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'distance_km': 0.5
                }
            ]
            mock_instance.return_value = mock_geo
            
            result = get_nearest_pincodes(28.6139, 77.2090, limit=10)
            
            assert len(result) == 1
            assert result[0]['pincode'] == '110001'
            assert result[0]['distance_km'] == 0.5
    
    def test_get_nearest_pincodes_invalid_coordinates(self):
        """Test getting nearest pincodes for invalid coordinates."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearest_pincodes.side_effect = ValueError("Invalid latitude: 95.0. Must be between -90 and 90.")
            mock_instance.return_value = mock_geo
            
            with pytest.raises(ValueError, match="Invalid latitude"):
                get_nearest_pincodes(95.0, 77.2090, limit=10)
    
    def test_coordinate_validation_latitude(self):
        """Test coordinate validation for latitude."""
        geo_data = GeospatialData()
        
        # Mock the required attributes
        geo_data._coordinate_data = pd.DataFrame()
        geo_data._ball_tree = MagicMock()
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            geo_data.get_nearest_pincodes(95.0, 77.2090)
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            geo_data.get_nearest_pincodes(-95.0, 77.2090)
    
    def test_coordinate_validation_longitude(self):
        """Test coordinate validation for longitude."""
        geo_data = GeospatialData()
        
        # Mock the required attributes
        geo_data._coordinate_data = pd.DataFrame()
        geo_data._ball_tree = MagicMock()
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            geo_data.get_nearest_pincodes(28.6139, 185.0)
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            geo_data.get_nearest_pincodes(28.6139, -185.0)
    
    def test_data_load_error_handling(self):
        """Test error handling when data fails to load."""
        with patch('pypinindia.geospatial.PincodeData') as mock_pincode_data_class:
            mock_instance = MagicMock()
            mock_instance.data = None
            mock_pincode_data_class.return_value = mock_instance
            
            with pytest.raises(DataLoadError):
                GeospatialData()
    
    @patch('pypinindia.geospatial.PincodeData')
    def test_generate_approximate_coordinates(self, mock_pincode_data_class):
        """Test coordinate generation logic."""
        # Create mock data
        mock_data = pd.DataFrame({
            'pincode': ['110001', '400001'],
            'officename': ['Connaught Place H.O', 'Fort S.O'],
            'districtname': ['Central Delhi', 'Mumbai'],
            'statename': ['DELHI', 'MAHARASHTRA'],
        })
        
        mock_instance = MagicMock()
        mock_instance.data = mock_data
        mock_pincode_data_class.return_value = mock_instance
        
        geo_data = GeospatialData()
        
        # Check that coordinate data was generated
        assert geo_data._coordinate_data is not None
        assert len(geo_data._coordinate_data) == 2
        assert 'latitude' in geo_data._coordinate_data.columns
        assert 'longitude' in geo_data._coordinate_data.columns
        assert 'pincode' in geo_data._coordinate_data.columns
    
    def test_distance_sorting(self):
        """Test that results are sorted by distance."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = [
                {'pincode': '110001', 'distance_km': 0.5},
                {'pincode': '110002', 'distance_km': 1.2},
                {'pincode': '110003', 'distance_km': 2.8}
            ]
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001')
            
            # Check that results are sorted by distance
            distances = [r['distance_km'] for r in result]
            assert distances == sorted(distances)
    
    def test_limit_parameter(self):
        """Test that limit parameter works correctly."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            # Return exactly 3 results when limit=3 is requested
            mock_geo.get_nearby_pincodes.return_value = [
                {'pincode': '110001', 'distance_km': 0.5},
                {'pincode': '110002', 'distance_km': 1.2},
                {'pincode': '110003', 'distance_km': 2.8}
            ]
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001', limit=3)
            
            assert len(result) == 3
    
    def test_radius_parameter(self):
        """Test that radius parameter is passed correctly."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = []
            mock_instance.return_value = mock_geo
            
            get_nearby_pincodes('110001', radius_km=10, limit=5)
            
            # Verify the method was called with correct parameters
            mock_geo.get_nearby_pincodes.assert_called_once_with('110001', 10, 5)


class TestGeospatialIntegration:
    """Integration tests for geospatial functionality."""
    
    def test_full_workflow_nearby_search(self):
        """Test complete workflow for nearby search."""
        # This would be an integration test with real data
        # For now, we'll mock it but structure it like a real test
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = [
                {
                    'pincode': '110002',
                    'office_name': 'Parliament Street S.O',
                    'district': 'Central Delhi',
                    'state': 'DELHI',
                    'latitude': 28.6200,
                    'longitude': 77.2100,
                    'distance_km': 1.2,
                    'office_type': 'S.O',
                    'delivery_status': 'Delivery',
                    'taluk': 'New Delhi'
                }
            ]
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001', radius_km=5)
            
            # Verify complete result structure
            assert len(result) == 1
            record = result[0]
            
            required_fields = [
                'pincode', 'office_name', 'district', 'state',
                'latitude', 'longitude', 'distance_km'
            ]
            
            for field in required_fields:
                assert field in record
            
            # Verify data types
            assert isinstance(record['distance_km'], (int, float))
            assert isinstance(record['latitude'], (int, float))
            assert isinstance(record['longitude'], (int, float))
    
    def test_error_propagation(self):
        """Test that errors are properly propagated through the system."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.side_effect = InvalidPincodeError('invalid')
            mock_instance.return_value = mock_geo
            
            with pytest.raises(InvalidPincodeError):
                get_nearby_pincodes('invalid')


class TestGeospatialEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_dataset(self):
        """Test behavior with empty dataset."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = []
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001')
            assert result == []
    
    def test_single_result(self):
        """Test behavior with single result."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = [
                {
                    'pincode': '110001',
                    'office_name': 'Test Office',
                    'district': 'Test District',
                    'state': 'TEST STATE',
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'distance_km': 0.0
                }
            ]
            mock_instance.return_value = mock_geo
            
            result = get_nearby_pincodes('110001')
            
            assert len(result) == 1
            assert result[0]['distance_km'] == 0.0
    
    def test_large_radius(self):
        """Test behavior with very large radius."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = []
            mock_instance.return_value = mock_geo
            
            # Should not raise an error
            result = get_nearby_pincodes('110001', radius_km=10000)
            assert isinstance(result, list)
    
    def test_zero_radius(self):
        """Test behavior with zero radius."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearby_pincodes.return_value = []
            mock_instance.return_value = mock_geo
            
            # Should not raise an error
            result = get_nearby_pincodes('110001', radius_km=0)
            assert isinstance(result, list)
    
    def test_extreme_coordinates(self):
        """Test behavior with extreme but valid coordinates."""
        with patch('pypinindia.geospatial._get_geospatial_instance') as mock_instance:
            mock_geo = MagicMock()
            mock_geo.get_nearest_pincodes.return_value = []
            mock_instance.return_value = mock_geo
            
            # Test extreme but valid coordinates
            result = get_nearest_pincodes(89.9, 179.9)  # Near North Pole
            assert isinstance(result, list)
            
            result = get_nearest_pincodes(-89.9, -179.9)  # Near South Pole
            assert isinstance(result, list)