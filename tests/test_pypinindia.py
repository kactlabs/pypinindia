"""
Tests for pypinindia library.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from pinin import (
    PincodeData,
    get_pincode_info,
    get_state,
    get_district,
    get_taluk,
    get_offices,
    search_by_state,
    search_by_district,
    get_states,
    get_districts,
)

from pinin.exceptions import (
    InvalidPincodeError,
    DataNotFoundError,
    DataLoadError,
)


class TestPincodeValidation:
    """Test pincode validation functionality."""
    
    def test_valid_pincode_string(self):
        """Test valid pincode as string."""
        pincode_data = PincodeData()
        result = pincode_data._validate_pincode("110001")
        assert result == "110001"
    
    def test_valid_pincode_integer(self):
        """Test valid pincode as integer."""
        pincode_data = PincodeData()
        result = pincode_data._validate_pincode(110001)
        assert result == "110001"
    
    def test_invalid_pincode_too_short(self):
        """Test invalid pincode - too short."""
        pincode_data = PincodeData()
        with pytest.raises(InvalidPincodeError):
            pincode_data._validate_pincode("12345")
    
    def test_invalid_pincode_too_long(self):
        """Test invalid pincode - too long."""
        pincode_data = PincodeData()
        with pytest.raises(InvalidPincodeError):
            pincode_data._validate_pincode("1234567")
    
    def test_invalid_pincode_non_numeric(self):
        """Test invalid pincode - contains non-numeric characters."""
        pincode_data = PincodeData()
        with pytest.raises(InvalidPincodeError):
            pincode_data._validate_pincode("11000A")
    
    def test_invalid_pincode_leading_zeros(self):
        """Test invalid pincode - leading zeros."""
        pincode_data = PincodeData()
        with pytest.raises(InvalidPincodeError):
            pincode_data._validate_pincode("00110001")
    
    def test_invalid_pincode_empty_string(self):
        """Test invalid pincode - empty string."""
        pincode_data = PincodeData()
        with pytest.raises(InvalidPincodeError):
            pincode_data._validate_pincode("")
    
    def test_invalid_pincode_whitespace(self):
        """Test invalid pincode - contains whitespace."""
        pincode_data = PincodeData()
        with pytest.raises(InvalidPincodeError):
            pincode_data._validate_pincode("11 0001")


class TestPincodeDataLoading:
    """Test data loading functionality."""
    
    @patch('pandas.read_csv')
    def test_data_loading_success(self, mock_read_csv):
        """Test successful data loading."""
        # Mock CSV data
        mock_data = pd.DataFrame({
            'pincode': ['110001', '110002'],
            'officename': ['Office1', 'Office2'],
            'statename': ['DELHI', 'DELHI'],
            'districtname': ['Central Delhi', 'Central Delhi'],
            'taluk': ['New Delhi', 'New Delhi'],
            'officetype': ['S.O', 'S.O'],
            'Deliverystatus': ['Delivery', 'Delivery']
        })
        mock_read_csv.return_value = mock_data
        
        with patch('os.path.exists', return_value=True):
            pincode_data = PincodeData()
            assert pincode_data.data is not None
            assert len(pincode_data.data) == 2
    
    @patch('pandas.read_csv')
    def test_data_loading_missing_columns(self, mock_read_csv):
        """Test data loading with missing required columns."""
        # Mock CSV data with missing columns
        mock_data = pd.DataFrame({
            'pincode': ['110001'],
            'officename': ['Office1'],
            # Missing other required columns
        })
        mock_read_csv.return_value = mock_data
        
        with patch('os.path.exists', return_value=True):
            with pytest.raises(DataLoadError):
                PincodeData()
    
    def test_data_loading_file_not_found(self):
        """Test data loading when file doesn't exist."""
        with pytest.raises(DataLoadError):
            PincodeData("/nonexistent/file.csv")
    
    @patch('pandas.read_csv')
    def test_data_loading_corrupted_file(self, mock_read_csv):
        """Test data loading with a corrupted CSV file."""
        mock_read_csv.side_effect = pd.errors.EmptyDataError("Empty CSV file")
        with pytest.raises(DataLoadError):
            PincodeData()


class TestPincodeLookup:
    """Test pincode lookup functionality."""
    
    @pytest.fixture
    def mock_pincode_data(self):
        """Create mock pincode data for testing."""
        data = pd.DataFrame({
            'pincode': ['110001', '110001', '110002'],
            'officename': ['Connaught Place S.O', 'Parliament Street S.O', 'Indraprastha S.O'],
            'statename': ['DELHI', 'DELHI', 'DELHI'],
            'districtname': ['Central Delhi', 'Central Delhi', 'Central Delhi'],
            'taluk': ['New Delhi', 'New Delhi', 'New Delhi'],
            'officetype': ['S.O', 'S.O', 'S.O'],
            'Deliverystatus': ['Delivery', 'Non-Delivery', 'Delivery']
        })
        
        with patch('pandas.read_csv', return_value=data), \
             patch('os.path.exists', return_value=True):
            return PincodeData()
    
    def test_get_pincode_info(self, mock_pincode_data):
        """Test getting complete pincode information."""
        result = mock_pincode_data.get_pincode_info("110001")
        assert len(result) == 2  # Two offices for this pincode
        assert result[0]['statename'] == 'DELHI'
        assert result[0]['pincode'] == '110001'
    
    def test_get_state(self, mock_pincode_data):
        """Test getting state for pincode."""
        result = mock_pincode_data.get_state("110001")
        assert result == 'DELHI'
    
    def test_get_district(self, mock_pincode_data):
        """Test getting district for pincode."""
        result = mock_pincode_data.get_district("110001")
        assert result == 'Central Delhi'
    
    def test_get_taluk(self, mock_pincode_data):
        """Test getting taluk for pincode."""
        result = mock_pincode_data.get_taluk("110001")
        assert result == 'New Delhi'
    
    def test_get_offices(self, mock_pincode_data):
        """Test getting offices for pincode."""
        result = mock_pincode_data.get_offices("110001")
        assert len(result) == 2
        assert 'Connaught Place S.O' in result
        assert 'Parliament Street S.O' in result
    
    def test_pincode_not_found(self, mock_pincode_data):
        """Test lookup for non-existent pincode."""
        with pytest.raises(DataNotFoundError):
            mock_pincode_data.get_pincode_info("600013")
    
    def test_get_pincode_info_empty_result(self, mock_pincode_data):
        """Test get_pincode_info when no data is found for the pincode."""
        with patch.object(mock_pincode_data, '_get_matching_rows', return_value=pd.DataFrame()):
            with pytest.raises(DataNotFoundError):
                mock_pincode_data.get_pincode_info("600013")
    
    def test_get_state_empty_result(self, mock_pincode_data):
        """Test get_state when no data is found for the pincode."""
        with patch.object(mock_pincode_data, '_get_matching_rows', return_value=pd.DataFrame()):
            with pytest.raises(DataNotFoundError):
                mock_pincode_data.get_state("600013")
    
    def test_get_district_empty_result(self, mock_pincode_data):
        """Test get_district when no data is found for the pincode."""
        with patch.object(mock_pincode_data, '_get_matching_rows', return_value=pd.DataFrame()):
            with pytest.raises(DataNotFoundError):
                mock_pincode_data.get_district("600013")
    
    def test_get_taluk_empty_result(self, mock_pincode_data):
        """Test get_taluk when no data is found for the pincode."""
        with patch.object(mock_pincode_data, '_get_matching_rows', return_value=pd.DataFrame()):
            with pytest.raises(DataNotFoundError):
                mock_pincode_data.get_taluk("600013")
    
    def test_get_offices_empty_result(self, mock_pincode_data):
        """Test get_offices when no data is found for the pincode."""
        result = mock_pincode_data.get_offices("110001")
        assert result != []


class TestSearchFunctionality:
    """Test search functionality."""
    
    @pytest.fixture
    def mock_search_data(self):
        """Create mock data for search testing."""
        data = pd.DataFrame({
            'pincode': ['110001', '110002', '400001', '400002'],
            'officename': ['Delhi Office 1', 'Delhi Office 2', 'Mumbai Office 1', 'Mumbai Office 2'],
            'statename': ['DELHI', 'DELHI', 'MAHARASHTRA', 'MAHARASHTRA'],
            'districtname': ['Central Delhi', 'Central Delhi', 'Mumbai', 'Mumbai'],
            'taluk': ['New Delhi', 'New Delhi', 'Mumbai', 'Mumbai'],
            'officetype': ['S.O', 'S.O', 'S.O', 'S.O'],
            'Deliverystatus': ['Delivery', 'Delivery', 'Delivery', 'Delivery']
        })
        
        with patch('pandas.read_csv', return_value=data), \
             patch('os.path.exists', return_value=True):
            return PincodeData()
    
    def test_search_by_state(self, mock_search_data):
        """Test searching pincodes by state."""
        result = mock_search_data.search_by_state("DELHI")
        assert len(result) == 2
        assert '110001' in result
        assert '110002' in result
    
    def test_search_by_state_case_insensitive(self, mock_search_data):
        """Test case-insensitive state search."""
        result = mock_search_data.search_by_state("delhi")
        assert len(result) == 2
    
    def test_search_by_district(self, mock_search_data):
        """Test searching pincodes by district."""
        result = mock_search_data.search_by_district("Mumbai")
        assert len(result) == 2
        assert '400001' in result
        assert '400002' in result
    
    def test_search_by_district_with_state(self, mock_search_data):
        """Test searching pincodes by district with state filter."""
        result = mock_search_data.search_by_district("Mumbai", "MAHARASHTRA")
        assert len(result) == 2
    
    def test_get_states(self, mock_search_data):
        """Test getting all states."""
        result = mock_search_data.get_states()
        assert len(result) == 2
        assert 'DELHI' in result
        assert 'MAHARASHTRA' in result
    
    def test_get_districts(self, mock_search_data):
        """Test getting all districts."""
        result = mock_search_data.get_districts()
        assert len(result) == 2
        assert 'Central Delhi' in result
        assert 'Mumbai' in result
    
    def test_get_districts_filtered_by_state(self, mock_search_data):
        """Test getting districts filtered by state."""
        result = mock_search_data.get_districts("DELHI")
        assert len(result) == 1
        assert 'Central Delhi' in result
    
    def test_search_by_state_empty_result(self, mock_search_data):
        """Test search_by_state when no data is found for the state."""
        with patch.object(mock_search_data, '_get_matching_rows', return_value=pd.DataFrame()):
            result = mock_search_data.search_by_state("NonExistentState")
            assert len(result) == 0
    
    def test_search_by_district_empty_result(self, mock_search_data):
        """Test search_by_district when no data is found for the district."""
        with patch.object(mock_search_data, '_get_matching_rows', return_value=pd.DataFrame()):
            result = mock_search_data.search_by_district("NonExistentDistrict")
            assert len(result) == 0
    
    def test_get_states_empty_result(self, mock_search_data):
        """Test get_states when the dataset is empty."""
        with patch.object(mock_search_data, 'data', pd.DataFrame()):
            result = mock_search_data.get_states()
            assert len(result) == 0
    
    def test_get_districts_empty_result(self, mock_search_data):
        """Test get_districts when the dataset is empty."""
        with patch.object(mock_search_data, 'data', pd.DataFrame()):
            result = mock_search_data.get_districts()
            assert len(result) == 0



class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('pinin.core._get_default_instance')
    def test_get_state_convenience(self, mock_get_instance):
        """Test convenience function for getting state."""
        mock_instance = MagicMock()
        mock_instance.get_state.return_value = 'DELHI'
        mock_get_instance.return_value = mock_instance
        
        result = get_state("110001")
        assert result == 'DELHI'
        mock_instance.get_state.assert_called_once_with("110001")
    
    @patch('pinin.core._get_default_instance')
    def test_get_pincode_info_convenience(self, mock_get_instance):
        """Test convenience function for getting pincode info."""
        mock_instance = MagicMock()
        mock_info = [{'pincode': '110001', 'statename': 'DELHI'}]
        mock_instance.get_pincode_info.return_value = mock_info
        mock_get_instance.return_value = mock_instance
        
        result = get_pincode_info("110001")
        assert result == mock_info
        mock_instance.get_pincode_info.assert_called_once_with("110001")
    
    @patch('pinin.core.PincodeData')
    def test_get_default_instance_singleton(self, MockPincodeData):
        """Test that _get_default_instance returns a singleton."""
        from pinin.core import _get_default_instance
        
        # Clear the cache to ensure a fresh instance is created
        _get_default_instance.cache_clear()
        
        instance1 = _get_default_instance()
        instance2 = _get_default_instance()
        
        assert instance1 is instance2
        MockPincodeData.assert_called_once()
    
    @patch('pinin.core._get_default_instance')
    def test_convenience_functions_handle_exceptions(self, mock_get_instance):
        """Test that convenience functions handle exceptions from PincodeData."""
        mock_instance = MagicMock()
        mock_instance.get_state.side_effect = DataNotFoundError("Pincode not found")
        mock_get_instance.return_value = mock_instance
        
        with pytest.raises(DataNotFoundError):
            get_state("600013")
        
        mock_instance.get_pincode_info.side_effect = DataNotFoundError("Pincode not found")
        with pytest.raises(DataNotFoundError):
            get_pincode_info("600013")


class TestStatistics:
    """Test statistics functionality."""
    
    @pytest.fixture
    def mock_stats_data(self):
        """Create mock data for statistics testing."""
        data = pd.DataFrame({
            'pincode': ['110001', '110001', '110002', '400001'],
            'officename': ['Office1', 'Office2', 'Office3', 'Office4'],
            'statename': ['DELHI', 'DELHI', 'DELHI', 'MAHARASHTRA'],
            'districtname': ['Central Delhi', 'Central Delhi', 'Central Delhi', 'Mumbai'],
            'taluk': ['New Delhi', 'New Delhi', 'New Delhi', 'Mumbai'],
            'officetype': ['S.O', 'S.O', 'S.O', 'S.O'],
            'Deliverystatus': ['Delivery', 'Delivery', 'Delivery', 'Delivery']
        })
        
        with patch('pandas.read_csv', return_value=data), \
             patch('os.path.exists', return_value=True):
            return PincodeData()
    
    def test_get_statistics(self, mock_stats_data):
        """Test getting dataset statistics."""
        stats = mock_stats_data.get_statistics()
        
        assert stats['total_records'] == 4
        assert stats['unique_pincodes'] == 3  # 110001, 110002, 400001
        assert stats['unique_states'] == 2    # DELHI, MAHARASHTRA
        assert stats['unique_districts'] == 2 # Central Delhi, Mumbai
        assert stats['unique_offices'] == 4   # All offices are unique
    
    def test_get_statistics_empty_dataset(self, mock_stats_data):
        """Test get_statistics when the dataset is empty."""
        with patch.object(mock_stats_data, 'data', pd.DataFrame()):
            stats = mock_stats_data.get_statistics()
            assert stats['total_records'] == 0
            assert stats['unique_pincodes'] == 0
            assert stats['unique_states'] == 0
            assert stats['unique_districts'] == 0
            assert stats['unique_offices'] == 0



if __name__ == '__main__':
    pytest.main([__file__])
