"""
Geospatial functionality for pypinindia - distance-based pincode search.
"""

import math
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from sklearn.neighbors import BallTree
import numpy as np

from .core import PincodeData
from .exceptions import InvalidPincodeError, DataNotFoundError, DataLoadError


class GeospatialData:
    """
    Handles geospatial operations for Indian pincode data.
    
    Provides functionality for:
    - Distance-based pincode search
    - Nearest pincode lookup by coordinates
    - Haversine distance calculations
    """
    
    def __init__(self, pincode_data: Optional[PincodeData] = None, use_geocoding: bool = False):
        """
        Initialize geospatial data handler.
        
        Args:
            pincode_data: PincodeData instance. If None, creates a new one.
            use_geocoding: If True, use real geocoding (slow). If False, use approximate coordinates (fast).
        """
        self.pincode_data = pincode_data or PincodeData()
        self._coordinate_data: Optional[pd.DataFrame] = None
        self._ball_tree: Optional[BallTree] = None
        self.use_geocoding = use_geocoding
        self._geocode_cache: Dict[str, Tuple[float, float]] = {}
        self._load_coordinate_data()
    
    def _load_coordinate_data(self) -> None:
        """Load and prepare coordinate data for geospatial operations."""
        if self.pincode_data.data is None:
            raise DataLoadError("Base pincode data not loaded")
        
        # Use approximate coordinates (fast) by default
        self._coordinate_data = self._generate_approximate_coordinates()
        self._build_spatial_index()
    
    def _geocode_pincode(self, pincode: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a pincode using geocoding.
        
        Args:
            pincode: The pincode to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut, GeocoderServiceError
            
            geolocator = Nominatim(user_agent="pypinindia")
            location = geolocator.geocode(f"{pincode}, India", timeout=10)
            
            if location:
                return (location.latitude, location.longitude)
        except ImportError:
            pass
        except (GeocoderTimedOut, GeocoderServiceError):
            pass
        
        return None
    
    def _generate_approximate_coordinates(self) -> pd.DataFrame:
        """
        Generate coordinates for pincodes using geocoding.
        
        Uses geopy's Nominatim geocoder to get real coordinates for each pincode.
        Falls back to district/state centroids if geocoding fails.
        """
        # Sample coordinate data for major Indian cities/districts
        # This is a minimal set for demonstration - expand as needed
        district_coordinates = {
            # Delhi
            ('Central Delhi', 'DELHI'): (28.6139, 77.2090),
            ('New Delhi', 'DELHI'): (28.6139, 77.2090),
            ('North Delhi', 'DELHI'): (28.7041, 77.1025),
            ('South Delhi', 'DELHI'): (28.5355, 77.2090),
            ('East Delhi', 'DELHI'): (28.6508, 77.2773),
            ('West Delhi', 'DELHI'): (28.6692, 77.1178),
            
            # Mumbai
            ('Mumbai', 'MAHARASHTRA'): (19.0760, 72.8777),
            ('Mumbai Suburban', 'MAHARASHTRA'): (19.0760, 72.8777),
            
            # Bangalore
            ('Bangalore', 'KARNATAKA'): (12.9716, 77.5946),
            ('Bengaluru Urban', 'KARNATAKA'): (12.9716, 77.5946),
            
            # Chennai
            ('Chennai', 'TAMIL NADU'): (13.0827, 80.2707),
            
            # Tamil Nadu districts
            ('Madurai', 'TAMIL NADU'): (9.9252, 78.1198),
            ('Coimbatore', 'TAMIL NADU'): (11.0168, 76.9558),
            ('Salem', 'TAMIL NADU'): (11.6643, 78.1460),
            ('Tiruchirappalli', 'TAMIL NADU'): (10.7905, 78.7047),
            ('Tirunelveli', 'TAMIL NADU'): (8.7139, 77.7567),
            ('Erode', 'TAMIL NADU'): (11.3410, 77.7172),
            ('Vellore', 'TAMIL NADU'): (12.9165, 79.1325),
            ('Thoothukudi', 'TAMIL NADU'): (8.7642, 78.1348),
            ('Dindigul', 'TAMIL NADU'): (10.3673, 77.9803),
            ('Thanjavur', 'TAMIL NADU'): (10.7870, 79.1378),
            ('Ranipet', 'TAMIL NADU'): (12.9222, 79.3333),
            ('Sivaganga', 'TAMIL NADU'): (9.8433, 78.4809),
            ('Karur', 'TAMIL NADU'): (10.9601, 78.0766),
            ('Ramanathapuram', 'TAMIL NADU'): (9.3639, 78.8370),
            ('Virudhunagar', 'TAMIL NADU'): (9.5810, 77.9624),
            ('Tiruppur', 'TAMIL NADU'): (11.1075, 77.3398),
            ('Cuddalore', 'TAMIL NADU'): (11.7480, 79.7714),
            ('Kanchipuram', 'TAMIL NADU'): (12.8342, 79.7036),
            ('Nagapattinam', 'TAMIL NADU'): (10.7658, 79.8448),
            ('Namakkal', 'TAMIL NADU'): (11.2189, 78.1677),
            ('Pudukkottai', 'TAMIL NADU'): (10.3833, 78.8000),
            ('Theni', 'TAMIL NADU'): (10.0104, 77.4977),
            ('Thiruvallur', 'TAMIL NADU'): (13.1143, 79.9074),
            ('Tiruvannamalai', 'TAMIL NADU'): (12.2253, 79.0747),
            ('Nilgiris', 'TAMIL NADU'): (11.4064, 76.6932),
            ('Perambalur', 'TAMIL NADU'): (11.2324, 78.8798),
            ('Ariyalur', 'TAMIL NADU'): (11.1401, 79.0770),
            ('Krishnagiri', 'TAMIL NADU'): (12.5186, 78.2137),
            ('Dharmapuri', 'TAMIL NADU'): (12.1211, 78.1582),
            ('Kanyakumari', 'TAMIL NADU'): (8.0883, 77.5385),
            ('Tambaram', 'TAMIL NADU'): (12.9229, 80.1275),
            
            # Kolkata
            ('Kolkata', 'WEST BENGAL'): (22.5726, 88.3639),
            
            # Hyderabad
            ('Hyderabad', 'TELANGANA'): (17.3850, 78.4867),
            
            # Pune
            ('Pune', 'MAHARASHTRA'): (18.5204, 73.8567),
            
            # Ahmedabad
            ('Ahmedabad', 'GUJARAT'): (23.0225, 72.5714),
            
            # Jaipur
            ('Jaipur', 'RAJASTHAN'): (26.9124, 75.7873),
            
            # Lucknow
            ('Lucknow', 'UTTAR PRADESH'): (26.8467, 80.9462),
            
            # Kanpur
            ('Kanpur Nagar', 'UTTAR PRADESH'): (26.4499, 80.3319),
            
            # Nagpur
            ('Nagpur', 'MAHARASHTRA'): (21.1458, 79.0882),
            
            # Indore
            ('Indore', 'MADHYA PRADESH'): (22.7196, 75.8577),
            
            # Thane
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),
            
            # Bhopal
            ('Bhopal', 'MADHYA PRADESH'): (23.2599, 77.4126),
            
            # Visakhapatnam
            ('Visakhapatnam', 'ANDHRA PRADESH'): (17.6868, 83.2185),
            
            # Pimpri-Chinchwad
            ('Pune', 'MAHARASHTRA'): (18.5204, 73.8567),  # Using Pune coordinates
            
            # Patna
            ('Patna', 'BIHAR'): (25.5941, 85.1376),
            
            # Vadodara
            ('Vadodara', 'GUJARAT'): (22.3072, 73.1812),
            
            # Ludhiana
            ('Ludhiana', 'PUNJAB'): (30.9010, 75.8573),
            
            # Agra
            ('Agra', 'UTTAR PRADESH'): (27.1767, 78.0081),
            
            # Nashik
            ('Nashik', 'MAHARASHTRA'): (19.9975, 73.7898),
            
            # Faridabad
            ('Faridabad', 'HARYANA'): (28.4089, 77.3178),
            
            # Meerut
            ('Meerut', 'UTTAR PRADESH'): (28.9845, 77.7064),
            
            # Rajkot
            ('Rajkot', 'GUJARAT'): (22.3039, 70.8022),
            
            # Kalyan-Dombivli
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),  # Using Thane coordinates
            
            # Vasai-Virar
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),  # Using Thane coordinates
            
            # Varanasi
            ('Varanasi', 'UTTAR PRADESH'): (25.3176, 82.9739),
            
            # Srinagar
            ('Srinagar', 'JAMMU & KASHMIR'): (34.0837, 74.7973),
            
            # Aurangabad
            ('Aurangabad', 'MAHARASHTRA'): (19.8762, 75.3433),
            
            # Dhanbad
            ('Dhanbad', 'JHARKHAND'): (23.7957, 86.4304),
            
            # Amritsar
            ('Amritsar', 'PUNJAB'): (31.6340, 74.8723),
            
            # Navi Mumbai
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),  # Using Thane coordinates
            
            # Allahabad
            ('Allahabad', 'UTTAR PRADESH'): (25.4358, 81.8463),
            
            # Ranchi
            ('Ranchi', 'JHARKHAND'): (23.3441, 85.3096),
            
            # Howrah
            ('Howrah', 'WEST BENGAL'): (22.5958, 88.2636),
            
            # Coimbatore
            ('Coimbatore', 'TAMIL NADU'): (11.0168, 76.9558),
            
            # Jabalpur
            ('Jabalpur', 'MADHYA PRADESH'): (23.1815, 79.9864),
            
            # Gwalior
            ('Gwalior', 'MADHYA PRADESH'): (26.2183, 78.1828),
            
            # Vijayawada
            ('Krishna', 'ANDHRA PRADESH'): (16.5062, 80.6480),
            
            # Jodhpur
            ('Jodhpur', 'RAJASTHAN'): (26.2389, 73.0243),
            
            # Madurai
            ('Madurai', 'TAMIL NADU'): (9.9252, 78.1198),
            
            # Raipur
            ('Raipur', 'CHHATTISGARH'): (21.2514, 81.6296),
            
            # Kota
            ('Kota', 'RAJASTHAN'): (25.2138, 75.8648),
            
            # Guwahati
            ('Kamrup Metropolitan', 'ASSAM'): (26.1445, 91.7362),
            
            # Chandigarh
            ('Chandigarh', 'CHANDIGARH'): (30.7333, 76.7794),
            
            # Solapur
            ('Solapur', 'MAHARASHTRA'): (17.6599, 75.9064),
            
            # Hubli-Dharwad
            ('Dharwad', 'KARNATAKA'): (15.4589, 75.0078),
            
            # Bareilly
            ('Bareilly', 'UTTAR PRADESH'): (28.3670, 79.4304),
            
            # Moradabad
            ('Moradabad', 'UTTAR PRADESH'): (28.8386, 78.7733),
            
            # Mysore
            ('Mysuru', 'KARNATAKA'): (12.2958, 76.6394),
            
            # Gurgaon
            ('Gurgaon', 'HARYANA'): (28.4595, 77.0266),
            
            # Aligarh
            ('Aligarh', 'UTTAR PRADESH'): (27.8974, 78.0880),
            
            # Jalandhar
            ('Jalandhar', 'PUNJAB'): (31.3260, 75.5762),
            
            # Tiruchirappalli
            ('Tiruchirappalli', 'TAMIL NADU'): (10.7905, 78.7047),
            
            # Bhubaneswar
            ('Khordha', 'ODISHA'): (20.2961, 85.8245),
            
            # Salem
            ('Salem', 'TAMIL NADU'): (11.6643, 78.1460),
            
            # Warangal
            ('Warangal Urban', 'TELANGANA'): (17.9689, 79.5941),
            
            # Mira-Bhayandar
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),  # Using Thane coordinates
            
            # Thiruvananthapuram
            ('Thiruvananthapuram', 'KERALA'): (8.5241, 76.9366),
            
            # Bhiwandi
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),  # Using Thane coordinates
            
            # Saharanpur
            ('Saharanpur', 'UTTAR PRADESH'): (29.9680, 77.5552),
            
            # Gorakhpur
            ('Gorakhpur', 'UTTAR PRADESH'): (26.7606, 83.3732),
            
            # Guntur
            ('Guntur', 'ANDHRA PRADESH'): (16.3067, 80.4365),
            
            # Bikaner
            ('Bikaner', 'RAJASTHAN'): (28.0229, 73.3119),
            
            # Amravati
            ('Amravati', 'MAHARASHTRA'): (20.9374, 77.7796),
            
            # Noida
            ('Gautam Buddha Nagar', 'UTTAR PRADESH'): (28.5355, 77.3910),
            
            # Jamshedpur
            ('East Singhbhum', 'JHARKHAND'): (22.8046, 86.2029),
            
            # Bhilai Nagar
            ('Durg', 'CHHATTISGARH'): (21.1938, 81.3509),
            
            # Cuttack
            ('Cuttack', 'ODISHA'): (20.4625, 85.8828),
            
            # Firozabad
            ('Firozabad', 'UTTAR PRADESH'): (27.1592, 78.3957),
            
            # Kochi
            ('Ernakulam', 'KERALA'): (9.9312, 76.2673),
            
            # Bhavnagar
            ('Bhavnagar', 'GUJARAT'): (21.7645, 72.1519),
            
            # Dehradun
            ('Dehradun', 'UTTARAKHAND'): (30.3165, 78.0322),
            
            # Durgapur
            ('Paschim Bardhaman', 'WEST BENGAL'): (23.5204, 87.3119),
            
            # Asansol
            ('Paschim Bardhaman', 'WEST BENGAL'): (23.6739, 86.9524),
            
            # Nanded
            ('Nanded', 'MAHARASHTRA'): (19.1383, 77.2975),
            
            # Kolhapur
            ('Kolhapur', 'MAHARASHTRA'): (16.7050, 74.2433),
            
            # Ajmer
            ('Ajmer', 'RAJASTHAN'): (26.4499, 74.6399),
            
            # Akola
            ('Akola', 'MAHARASHTRA'): (20.7002, 77.0082),
            
            # Gulbarga
            ('Kalaburagi', 'KARNATAKA'): (17.3297, 76.8343),
            
            # Jamnagar
            ('Jamnagar', 'GUJARAT'): (22.4707, 70.0577),
            
            # Ujjain
            ('Ujjain', 'MADHYA PRADESH'): (23.1765, 75.7885),
            
            # Loni
            ('Ghaziabad', 'UTTAR PRADESH'): (28.6692, 77.4538),
            
            # Siliguri
            ('Darjeeling', 'WEST BENGAL'): (26.7271, 88.3953),
            
            # Jhansi
            ('Jhansi', 'UTTAR PRADESH'): (25.4484, 78.5685),
            
            # Ulhasnagar
            ('Thane', 'MAHARASHTRA'): (19.2183, 72.9781),  # Using Thane coordinates
            
            # Jammu
            ('Jammu', 'JAMMU & KASHMIR'): (32.7266, 74.8570),
            
            # Sangli-Miraj & Kupwad
            ('Sangli', 'MAHARASHTRA'): (16.8524, 74.5815),
            
            # Mangalore
            ('Dakshina Kannada', 'KARNATAKA'): (12.9141, 74.8560),
            
            # Erode
            ('Erode', 'TAMIL NADU'): (11.3410, 77.7172),
            
            # Belgaum
            ('Belagavi', 'KARNATAKA'): (15.8497, 74.4977),
            
            # Ambattur
            ('Thiruvallur', 'TAMIL NADU'): (13.1143, 80.1548),
            
            # Tirunelveli
            ('Tirunelveli', 'TAMIL NADU'): (8.7139, 77.7567),
            
            # Malegaon
            ('Nashik', 'MAHARASHTRA'): (19.9975, 73.7898),  # Using Nashik coordinates
            
            # Gaya
            ('Gaya', 'BIHAR'): (24.7914, 85.0002),
            
            # Jalgaon
            ('Jalgaon', 'MAHARASHTRA'): (21.0077, 75.5626),
            
            # Udaipur
            ('Udaipur', 'RAJASTHAN'): (24.5854, 73.7125),
            
            # Maheshtala
            ('South 24 Parganas', 'WEST BENGAL'): (22.5048, 88.2434),
        }
        
        # State centroids for fallback when district is not found
        state_coordinates = {
            'ANDHRA PRADESH': (15.9129, 79.7400),
            'ARUNACHAL PRADESH': (28.2180, 94.7278),
            'ASSAM': (26.2006, 92.9376),
            'BIHAR': (25.0961, 85.3131),
            'CHHATTISGARH': (21.2787, 81.8661),
            'GOA': (15.2993, 74.1240),
            'GUJARAT': (23.0225, 72.5714),
            'HARYANA': (29.0588, 76.0856),
            'HIMACHAL PRADESH': (31.1048, 77.1734),
            'JHARKHAND': (23.6102, 85.2799),
            'KARNATAKA': (15.3173, 75.7139),
            'KERALA': (10.8505, 76.2711),
            'MADHYA PRADESH': (22.9734, 78.6569),
            'MAHARASHTRA': (19.7515, 75.7139),
            'MANIPUR': (24.6637, 93.9063),
            'MEGHALAYA': (25.4670, 91.3662),
            'MIZORAM': (23.1645, 92.9376),
            'NAGALAND': (26.1584, 94.5624),
            'ODISHA': (20.9517, 85.0985),
            'PUNJAB': (31.1471, 75.3412),
            'RAJASTHAN': (27.0238, 74.2179),
            'SIKKIM': (27.5330, 88.5122),
            'TAMIL NADU': (11.1271, 78.6569),
            'TELANGANA': (18.1124, 79.0193),
            'TRIPURA': (23.9408, 91.9882),
            'UTTAR PRADESH': (26.8467, 80.9462),
            'UTTARAKHAND': (30.0668, 79.0193),
            'WEST BENGAL': (22.9868, 87.8550),
            'ANDAMAN & NICOBAR ISLANDS': (11.7401, 92.6586),
            'CHANDIGARH': (30.7333, 76.7794),
            'DADRA & NAGAR HAVELI': (20.1809, 73.0169),
            'DAMAN & DIU': (20.4283, 72.8397),
            'DELHI': (28.7041, 77.1025),
            'JAMMU & KASHMIR': (34.0837, 74.7973),
            'LADAKH': (34.1526, 77.5771),
            'LAKSHADWEEP': (10.5667, 72.6417),
            'PUDUCHERRY': (11.9416, 79.8083),
        }
        
        # Create coordinate mapping for each pincode
        coordinate_data = []
        
        if self.use_geocoding:
            # Get unique pincodes to avoid redundant geocoding
            unique_pincodes = self.pincode_data.data['pincode'].unique()
            
            print(f"Geocoding {len(unique_pincodes)} unique pincodes (this will take time)...")
            
            for idx, pincode in enumerate(unique_pincodes):
                if idx % 100 == 0 and idx > 0:
                    print(f"Processed {idx}/{len(unique_pincodes)} pincodes...")
                
                # Try geocoding first
                coords = self._geocode_pincode(pincode)
                
                if coords is None:
                    # Fallback to district/state coordinates
                    pincode_rows = self.pincode_data.data[self.pincode_data.data['pincode'] == pincode]
                    if not pincode_rows.empty:
                        row = pincode_rows.iloc[0]
                        district = row['districtname']
                        state = row['statename']
                        
                        coords = district_coordinates.get((district, state))
                        if coords is None:
                            coords = state_coordinates.get(state)
                        if coords is None:
                            coords = (20.5937, 78.9629)
                        
                        lat_variation = (hash(pincode + district) % 1000) / 100000.0 - 0.005
                        lon_variation = (hash(pincode + state) % 1000) / 100000.0 - 0.005
                        coords = (coords[0] + lat_variation, coords[1] + lon_variation)
                
                self._geocode_cache[pincode] = coords
            
            print(f"Geocoding complete. Building coordinate dataset...")
            
            # Build coordinate data using cached geocoded results
            for _, row in self.pincode_data.data.iterrows():
                pincode = row['pincode']
                coords = self._geocode_cache.get(pincode, (20.5937, 78.9629))
                
                coordinate_data.append({
                    'pincode': pincode,
                    'latitude': coords[0],
                    'longitude': coords[1],
                    'district': row['districtname'],
                    'state': row['statename'],
                    'officename': row['officename']
                })
        else:
            # Fast mode: use district/state centroids with variations
            for _, row in self.pincode_data.data.iterrows():
                district = row['districtname']
                state = row['statename']
                pincode = row['pincode']
                
                # Try to find coordinates by district first
                coords = district_coordinates.get((district, state))
                
                # Fallback to state coordinates if district not found
                if coords is None:
                    coords = state_coordinates.get(state)
                
                # If still no coordinates, use a default (center of India)
                if coords is None:
                    coords = (20.5937, 78.9629)
                
                # Add variation based on pincode to spread out locations
                lat_variation = (hash(pincode + district) % 1000) / 100000.0 - 0.005
                lon_variation = (hash(pincode + state) % 1000) / 100000.0 - 0.005
                
                coordinate_data.append({
                    'pincode': pincode,
                    'latitude': coords[0] + lat_variation,
                    'longitude': coords[1] + lon_variation,
                    'district': district,
                    'state': state,
                    'officename': row['officename']
                })
        
        return pd.DataFrame(coordinate_data)
    
    def _build_spatial_index(self) -> None:
        """Build spatial index for efficient nearest neighbor queries."""
        if self._coordinate_data is None:
            return
        
        # Convert coordinates to radians for BallTree
        coords_rad = np.radians(
            self._coordinate_data[['latitude', 'longitude']].values
        )
        
        # Build BallTree with haversine metric
        self._ball_tree = BallTree(coords_rad, metric='haversine')
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth.
        
        Args:
            lat1, lon1: Latitude and longitude of first point in decimal degrees
            lat2, lon2: Latitude and longitude of second point in decimal degrees
            
        Returns:
            Distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in kilometers
        r = 6371
        
        return c * r
    
    def get_nearby_pincodes(self, pincode: Union[str, int], radius_km: float = 5, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find pincodes within a specified radius of a given pincode.
        
        Args:
            pincode: Reference pincode
            radius_km: Search radius in kilometers (default: 5)
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            List of dictionaries containing nearby pincode information,
            sorted by distance
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If pincode not found
        """
        if self._coordinate_data is None or self._ball_tree is None:
            raise DataLoadError("Coordinate data not loaded")
        
        # Validate and get coordinates for the reference pincode
        pincode_str = self.pincode_data._validate_pincode(pincode)
        
        ref_coords = self._coordinate_data[
            self._coordinate_data['pincode'] == pincode_str
        ]
        
        if ref_coords.empty:
            raise DataNotFoundError(pincode_str)
        
        # Get the first matching coordinate (in case of multiple offices)
        ref_lat = ref_coords.iloc[0]['latitude']
        ref_lon = ref_coords.iloc[0]['longitude']
        
        # Use get_nearest_pincodes with max_distance filter
        all_results = self.get_nearest_pincodes(ref_lat, ref_lon, limit * 10, radius_km)
        
        # Filter to unique pincodes only (exclude the reference pincode)
        seen_pincodes = set([pincode_str])
        unique_results = []
        
        for result in all_results:
            if result['pincode'] not in seen_pincodes:
                seen_pincodes.add(result['pincode'])
                unique_results.append(result)
                if len(unique_results) >= limit:
                    break
        
        return unique_results
    
    def get_nearest_pincodes(self, latitude: float, longitude: float, 
                           limit: int = 10, max_distance_km: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Find nearest pincodes to given coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            limit: Maximum number of results to return (default: 10)
            max_distance_km: Maximum distance in kilometers (optional)
            
        Returns:
            List of dictionaries containing nearest pincode information,
            sorted by distance
        """
        if self._coordinate_data is None or self._ball_tree is None:
            raise DataLoadError("Coordinate data not loaded")
        
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
        
        # Convert query point to radians
        query_point = np.radians([[latitude, longitude]])
        
        # Query the spatial index
        if max_distance_km:
            # Convert max distance to radians
            max_distance_rad = max_distance_km / 6371.0
            indices = self._ball_tree.query_radius(query_point, r=max_distance_rad)[0]
            
            if len(indices) == 0:
                return []
            
            # Calculate actual distances for all points within radius
            distances_km = []
            for idx in indices:
                coord_row = self._coordinate_data.iloc[idx]
                dist = self.haversine_distance(
                    latitude, longitude,
                    coord_row['latitude'], coord_row['longitude']
                )
                distances_km.append(dist)
            
            # Sort by distance and limit
            sorted_pairs = sorted(zip(distances_km, indices), key=lambda x: x[0])
            distances_km = [d for d, _ in sorted_pairs[:limit]]
            indices = [i for _, i in sorted_pairs[:limit]]
        else:
            # Find k nearest neighbors
            distances_rad, indices = self._ball_tree.query(query_point, k=limit)
            distances_km = (distances_rad[0] * 6371.0).tolist()
            indices = indices[0].tolist()
        
        # Build result list
        results = []
        for i, idx in enumerate(indices):
            if i >= limit:
                break
                
            coord_row = self._coordinate_data.iloc[idx]
            
            # Get additional pincode information
            pincode_info = self.pincode_data.get_pincode_info(coord_row['pincode'])
            
            result = {
                'pincode': coord_row['pincode'],
                'office_name': coord_row['officename'],
                'district': coord_row['district'],
                'state': coord_row['state'],
                'latitude': coord_row['latitude'],
                'longitude': coord_row['longitude'],
                'distance_km': round(distances_km[i], 2)
            }
            
            # Add additional info from the first matching office
            if pincode_info:
                result.update({
                    'office_type': pincode_info[0].get('officetype', ''),
                    'delivery_status': pincode_info[0].get('Deliverystatus', ''),
                    'taluk': pincode_info[0].get('taluk', '')
                })
            
            results.append(result)
        
        # Sort by distance
        results.sort(key=lambda x: x['distance_km'])
        
        return results
    
    def get_pincode_coordinates(self, pincode: Union[str, int]) -> Dict[str, Any]:
        """
        Get coordinates for a specific pincode.
        
        Args:
            pincode: The pincode to lookup
            
        Returns:
            Dictionary containing coordinate information
            
        Raises:
            InvalidPincodeError: If pincode format is invalid
            DataNotFoundError: If pincode not found
        """
        if self._coordinate_data is None:
            raise DataLoadError("Coordinate data not loaded")
        
        pincode_str = self.pincode_data._validate_pincode(pincode)
        
        coords = self._coordinate_data[
            self._coordinate_data['pincode'] == pincode_str
        ]
        
        if coords.empty:
            raise DataNotFoundError(pincode_str)
        
        # Return the first matching coordinate
        coord_row = coords.iloc[0]
        return {
            'pincode': coord_row['pincode'],
            'latitude': coord_row['latitude'],
            'longitude': coord_row['longitude'],
            'district': coord_row['district'],
            'state': coord_row['state']
        }


# Singleton instance for convenience functions
_geospatial_instance: Optional[GeospatialData] = None


def _get_geospatial_instance() -> GeospatialData:
    """Get or create singleton GeospatialData instance."""
    global _geospatial_instance
    if _geospatial_instance is None:
        _geospatial_instance = GeospatialData()
    return _geospatial_instance


# Convenience functions
def get_nearby_pincodes(pincode: Union[str, int], radius_km: float = 5, 
                       limit: int = 10) -> List[Dict[str, Any]]:
    """
    Find pincodes within a specified radius of a given pincode.
    
    Args:
        pincode: Reference pincode
        radius_km: Search radius in kilometers (default: 5)
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        List of dictionaries containing nearby pincode information,
        sorted by distance
    """
    return _get_geospatial_instance().get_nearby_pincodes(pincode, radius_km, limit)


def get_nearest_pincodes(latitude: float, longitude: float, 
                        limit: int = 10) -> List[Dict[str, Any]]:
    """
    Find nearest pincodes to given coordinates.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        List of dictionaries containing nearest pincode information,
        sorted by distance
    """
    return _get_geospatial_instance().get_nearest_pincodes(latitude, longitude, limit)


def get_pincode_coordinates(pincode: Union[str, int]) -> Dict[str, Any]:
    """
    Get coordinates for a specific pincode.
    
    Args:
        pincode: The pincode to lookup
        
    Returns:
        Dictionary containing coordinate information
    """
    return _get_geospatial_instance().get_pincode_coordinates(pincode)