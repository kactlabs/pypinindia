"""
Tests for CLI geospatial functionality in pypinindia.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from pypinindia.cli import main, handle_nearby_command, handle_nearest_command
from pypinindia.exceptions import InvalidPincodeError, DataNotFoundError


class TestCLIGeospatialCommands:
    """Test cases for CLI geospatial commands."""
    
    def test_nearby_command_help(self, capsys):
        """Test that nearby command appears in help."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--help']):
                main()
        
        captured = capsys.readouterr()
        assert '--nearby' in captured.out
        assert 'Find pincodes near the specified pincode' in captured.out
    
    def test_nearest_command_help(self, capsys):
        """Test that nearest command appears in help."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--help']):
                main()
        
        captured = capsys.readouterr()
        assert '--nearest' in captured.out
        assert 'Find nearest pincodes to coordinates' in captured.out
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_nearby_command_success(self, mock_get_nearby, capsys):
        """Test successful nearby command execution."""
        mock_get_nearby.return_value = [
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
        
        with patch('sys.argv', ['pypinindia', '--nearby', '110001', '--radius', '5']):
            main()
        
        captured = capsys.readouterr()
        assert 'Parliament Street S.O' in captured.out
        assert '1.2' in captured.out
        mock_get_nearby.assert_called_once_with('110001', 5.0, 10)
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_nearby_command_json_output(self, mock_get_nearby, capsys):
        """Test nearby command with JSON output."""
        mock_result = [
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
        mock_get_nearby.return_value = mock_result
        
        with patch('sys.argv', ['pypinindia', '--nearby', '110001', '--json']):
            main()
        
        captured = capsys.readouterr()
        # Should be valid JSON
        result = json.loads(captured.out)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['pincode'] == '110002'
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_nearby_command_no_results(self, mock_get_nearby, capsys):
        """Test nearby command when no results found."""
        mock_get_nearby.return_value = []
        
        with patch('sys.argv', ['pypinindia', '--nearby', '110001']):
            main()
        
        captured = capsys.readouterr()
        assert 'No pincodes found within' in captured.out
    
    @patch('pypinindia.cli.get_nearest_pincodes')
    def test_nearest_command_success(self, mock_get_nearest, capsys):
        """Test successful nearest command execution."""
        mock_get_nearest.return_value = [
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
        
        with patch('sys.argv', ['pypinindia', '--nearest', '--lat', '28.6139', '--lon', '77.2090']):
            main()
        
        captured = capsys.readouterr()
        assert 'Connaught Place H.O' in captured.out
        assert '0.5' in captured.out
        mock_get_nearest.assert_called_once_with(28.6139, 77.2090, 10)
    
    @patch('pypinindia.cli.get_nearest_pincodes')
    def test_nearest_command_with_limit(self, mock_get_nearest, capsys):
        """Test nearest command with custom limit."""
        mock_get_nearest.return_value = []
        
        with patch('sys.argv', ['pypinindia', '--nearest', '--lat', '28.6139', '--lon', '77.2090', '--limit', '5']):
            main()
        
        mock_get_nearest.assert_called_once_with(28.6139, 77.2090, 5)
    
    def test_nearest_command_missing_coordinates(self, capsys):
        """Test nearest command with missing coordinates."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearest']):
                main()
        
        captured = capsys.readouterr()
        assert 'Both --lat and --lon are required' in captured.err
    
    def test_nearest_command_missing_latitude(self, capsys):
        """Test nearest command with missing latitude."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearest', '--lon', '77.2090']):
                main()
        
        captured = capsys.readouterr()
        assert 'Both --lat and --lon are required' in captured.err
    
    def test_nearest_command_missing_longitude(self, capsys):
        """Test nearest command with missing longitude."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearest', '--lat', '28.6139']):
                main()
        
        captured = capsys.readouterr()
        assert 'Both --lat and --lon are required' in captured.err
    
    def test_nearby_command_invalid_pincode(self, capsys):
        """Test nearby command with invalid pincode."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearby', '12345']):  # 5 digits instead of 6
                main()
        
        captured = capsys.readouterr()
        assert 'Invalid pincode format' in captured.err
    
    def test_nearby_command_non_numeric_pincode(self, capsys):
        """Test nearby command with non-numeric pincode."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearby', 'abcdef']):
                main()
        
        captured = capsys.readouterr()
        assert 'Invalid pincode format' in captured.err
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_nearby_command_exception_handling(self, mock_get_nearby, capsys):
        """Test nearby command exception handling."""
        mock_get_nearby.side_effect = DataNotFoundError('110001')
        
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearby', '110001']):
                main()
        
        captured = capsys.readouterr()
        assert 'Error:' in captured.err
    
    @patch('pypinindia.cli.get_nearest_pincodes')
    def test_nearest_command_exception_handling(self, mock_get_nearest, capsys):
        """Test nearest command exception handling."""
        mock_get_nearest.side_effect = ValueError("Invalid coordinates")
        
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pypinindia', '--nearest', '--lat', '95.0', '--lon', '77.2090']):
                main()
        
        captured = capsys.readouterr()
        assert 'Error:' in captured.err
    
    def test_coordinates_flag_with_pincode(self, capsys):
        """Test --coordinates flag with pincode."""
        with patch('pypinindia.cli.get_pincode_coordinates') as mock_get_coords:
            mock_get_coords.return_value = {
                'pincode': '110001',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'district': 'Central Delhi',
                'state': 'DELHI'
            }
            
            with patch('sys.argv', ['pypinindia', '110001', '--coordinates']):
                main()
            
            captured = capsys.readouterr()
            assert '28.6139' in captured.out
            assert '77.2090' in captured.out
            mock_get_coords.assert_called_once_with('110001')


class TestCLIGeospatialHelpers:
    """Test helper functions for CLI geospatial commands."""
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_handle_nearby_command_success(self, mock_get_nearby, capsys):
        """Test handle_nearby_command function."""
        mock_get_nearby.return_value = [
            {
                'pincode': '110002',
                'office_name': 'Test Office',
                'district': 'Test District',
                'state': 'TEST STATE',
                'latitude': 28.6200,
                'longitude': 77.2100,
                'distance_km': 1.2
            }
        ]
        
        handle_nearby_command('110001', 5.0, 10, False, True, None)
        
        captured = capsys.readouterr()
        assert 'Pincodes within 5.0km of 110001' in captured.out
        assert 'Test Office' in captured.out
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_handle_nearby_command_no_results(self, mock_get_nearby, capsys):
        """Test handle_nearby_command with no results."""
        mock_get_nearby.return_value = []
        
        handle_nearby_command('110001', 5.0, 10, False, False, None)
        
        captured = capsys.readouterr()
        assert 'No pincodes found within 5.0km of 110001' in captured.out
    
    @patch('pypinindia.cli.get_nearby_pincodes')
    def test_handle_nearby_command_json(self, mock_get_nearby, capsys):
        """Test handle_nearby_command with JSON output."""
        mock_result = [
            {
                'pincode': '110002',
                'office_name': 'Test Office',
                'distance_km': 1.2
            }
        ]
        mock_get_nearby.return_value = mock_result
        
        handle_nearby_command('110001', 5.0, 10, True, False, None)
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert isinstance(result, list)
        assert result[0]['pincode'] == '110002'
    
    @patch('pypinindia.cli.get_nearest_pincodes')
    def test_handle_nearest_command_success(self, mock_get_nearest, capsys):
        """Test handle_nearest_command function."""
        mock_get_nearest.return_value = [
            {
                'pincode': '110001',
                'office_name': 'Test Office',
                'district': 'Test District',
                'state': 'TEST STATE',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'distance_km': 0.5
            }
        ]
        
        handle_nearest_command(28.6139, 77.2090, 10, False, True)
        
        captured = capsys.readouterr()
        assert 'Nearest pincodes to (28.6139, 77.209)' in captured.out
        assert 'Test Office' in captured.out
    
    @patch('pypinindia.cli.get_nearest_pincodes')
    def test_handle_nearest_command_no_results(self, mock_get_nearest, capsys):
        """Test handle_nearest_command with no results."""
        mock_get_nearest.return_value = []
        
        handle_nearest_command(28.6139, 77.2090, 10, False, False)
        
        captured = capsys.readouterr()
        assert 'No pincodes found near coordinates (28.6139, 77.209)' in captured.out
    
    @patch('pypinindia.cli.get_nearest_pincodes')
    def test_handle_nearest_command_json(self, mock_get_nearest, capsys):
        """Test handle_nearest_command with JSON output."""
        mock_result = [
            {
                'pincode': '110001',
                'office_name': 'Test Office',
                'distance_km': 0.5
            }
        ]
        mock_get_nearest.return_value = mock_result
        
        handle_nearest_command(28.6139, 77.2090, 10, True, False)
        
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert isinstance(result, list)
        assert result[0]['pincode'] == '110001'


class TestCLIGeospatialIntegration:
    """Integration tests for CLI geospatial functionality."""
    
    def test_nearby_command_full_workflow(self, capsys):
        """Test complete nearby command workflow."""
        with patch('pypinindia.cli.get_nearby_pincodes') as mock_get_nearby:
            mock_get_nearby.return_value = [
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
            
            with patch('sys.argv', ['pypinindia', '--nearby', '110001', '--radius', '10', '--limit', '5', '--verbose']):
                main()
            
            captured = capsys.readouterr()
            
            # Check that all expected information is displayed
            assert 'Parliament Street S.O' in captured.out
            assert 'Central Delhi' in captured.out
            assert 'DELHI' in captured.out
            assert '1.2' in captured.out
            
            # Verify function was called with correct parameters
            mock_get_nearby.assert_called_once_with('110001', 10.0, 5)
    
    def test_nearest_command_full_workflow(self, capsys):
        """Test complete nearest command workflow."""
        with patch('pypinindia.cli.get_nearest_pincodes') as mock_get_nearest:
            mock_get_nearest.return_value = [
                {
                    'pincode': '110001',
                    'office_name': 'Connaught Place H.O',
                    'district': 'Central Delhi',
                    'state': 'DELHI',
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'distance_km': 0.0,
                    'office_type': 'H.O',
                    'delivery_status': 'Delivery',
                    'taluk': 'New Delhi'
                }
            ]
            
            with patch('sys.argv', ['pypinindia', '--nearest', '--lat', '28.6139', '--lon', '77.2090', '--limit', '3', '--verbose']):
                main()
            
            captured = capsys.readouterr()
            
            # Check that all expected information is displayed
            assert 'Connaught Place H.O' in captured.out
            assert 'Central Delhi' in captured.out
            assert 'DELHI' in captured.out
            assert '0.0' in captured.out
            
            # Verify function was called with correct parameters
            mock_get_nearest.assert_called_once_with(28.6139, 77.2090, 3)
    
    def test_error_handling_integration(self, capsys):
        """Test error handling in CLI integration."""
        with patch('pypinindia.cli.get_nearby_pincodes') as mock_get_nearby:
            mock_get_nearby.side_effect = InvalidPincodeError('110001')
            
            with pytest.raises(SystemExit):
                with patch('sys.argv', ['pypinindia', '--nearby', '110001']):
                    main()
            
            captured = capsys.readouterr()
            assert 'Error:' in captured.err
            assert 'Invalid pincode' in captured.err


class TestCLIGeospatialEdgeCases:
    """Test edge cases for CLI geospatial functionality."""
    
    def test_nearby_with_zero_radius(self, capsys):
        """Test nearby command with zero radius."""
        with patch('pypinindia.cli.get_nearby_pincodes') as mock_get_nearby:
            mock_get_nearby.return_value = []
            
            with patch('sys.argv', ['pypinindia', '--nearby', '110001', '--radius', '0']):
                main()
            
            mock_get_nearby.assert_called_once_with('110001', 0.0, 10)
    
    def test_nearby_with_large_radius(self, capsys):
        """Test nearby command with very large radius."""
        with patch('pypinindia.cli.get_nearby_pincodes') as mock_get_nearby:
            mock_get_nearby.return_value = []
            
            with patch('sys.argv', ['pypinindia', '--nearby', '110001', '--radius', '10000']):
                main()
            
            mock_get_nearby.assert_called_once_with('110001', 10000.0, 10)
    
    def test_nearest_with_extreme_coordinates(self, capsys):
        """Test nearest command with extreme but valid coordinates."""
        with patch('pypinindia.cli.get_nearest_pincodes') as mock_get_nearest:
            mock_get_nearest.return_value = []
            
            with patch('sys.argv', ['pypinindia', '--nearest', '--lat', '89.9', '--lon', '179.9']):
                main()
            
            mock_get_nearest.assert_called_once_with(89.9, 179.9, 10)
    
    def test_large_limit_parameter(self, capsys):
        """Test with very large limit parameter."""
        with patch('pypinindia.cli.get_nearby_pincodes') as mock_get_nearby:
            mock_get_nearby.return_value = []
            
            with patch('sys.argv', ['pypinindia', '--nearby', '110001', '--limit', '1000']):
                main()
            
            mock_get_nearby.assert_called_once_with('110001', 5.0, 1000)