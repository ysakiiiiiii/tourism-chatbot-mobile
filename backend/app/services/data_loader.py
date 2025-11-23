import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Optional
from app.config import settings

class DataLoader:
    def __init__(self):
        self.excel_path = Path("/data/ilocos_chatbot_dataset.xlsx")
        self.tourist_spots: List[Dict] = []
        self.cuisines: List[Dict] = []
        self.load_data()
    
    def load_data(self):
        """Load data from Excel file"""
        try:
            if not self.excel_path.exists():
                print(f"Warning: Excel file not found at {self.excel_path}")
                return
            
            # Read Excel file
            df = pd.read_excel(self.excel_path)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Separate tourist spots and cuisines
            tourist_spots_df = df[df['type'] == 'tourist_spot']
            cuisines_df = df[df['type'] == 'cuisine']
            
            # Convert to list of dictionaries
            self.tourist_spots = tourist_spots_df.to_dict('records')
            self.cuisines = cuisines_df.to_dict('records')
            
            # Clean NaN values
            self.tourist_spots = self._clean_nan(self.tourist_spots)
            self.cuisines = self._clean_nan(self.cuisines)
            
            print(f"Loaded {len(self.tourist_spots)} tourist spots and {len(self.cuisines)} cuisines")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.tourist_spots = []
            self.cuisines = []
    
    def _clean_nan(self, data: List[Dict]) -> List[Dict]:
        """Replace NaN values with None or empty string"""
        cleaned = []
        for item in data:
            cleaned_item = {}
            for key, value in item.items():
                if pd.isna(value):
                    cleaned_item[key] = None
                else:
                    cleaned_item[key] = str(value) if not isinstance(value, str) else value
            cleaned.append(cleaned_item)
        return cleaned
    
    def get_all_tourist_spots(self) -> List[Dict]:
        """Get all tourist spots"""
        return self.tourist_spots
    
    def get_all_cuisines(self) -> List[Dict]:
        """Get all cuisines"""
        return self.cuisines
    
    def get_tourist_spot_by_id(self, spot_id: str) -> Optional[Dict]:
        """Get tourist spot by ID"""
        for spot in self.tourist_spots:
            if spot.get('id') == spot_id:
                return spot
        return None
    
    def get_cuisine_by_id(self, cuisine_id: str) -> Optional[Dict]:
        """Get cuisine by ID"""
        for cuisine in self.cuisines:
            if cuisine.get('id') == cuisine_id:
                return cuisine
        return None
    
    def search_by_keyword(self, keyword: str) -> Dict[str, List[Dict]]:
        """Search both tourist spots and cuisines by keyword"""
        keyword_lower = keyword.lower()
        
        matching_spots = []
        matching_cuisines = []
        
        for spot in self.tourist_spots:
            if self._matches_keyword(spot, keyword_lower):
                matching_spots.append(spot)
        
        for cuisine in self.cuisines:
            if self._matches_keyword(cuisine, keyword_lower):
                matching_cuisines.append(cuisine)
        
        return {
            "tourist_spots": matching_spots,
            "cuisines": matching_cuisines
        }
    
    def _matches_keyword(self, item: Dict, keyword: str) -> bool:
        """Check if item matches keyword"""
        searchable_fields = ['name', 'location', 'description_keywords', 'full_description', 'related_items']
        
        for field in searchable_fields:
            value = item.get(field)
            if value and isinstance(value, str) and keyword in value.lower():
                return True
        return False
    
    def add_tourist_spot(self, spot_data: Dict) -> Dict:
        """Add new tourist spot"""
        # Generate new ID
        existing_ids = [int(s['id'][1:]) for s in self.tourist_spots if s['id'].startswith('TS')]
        new_id = f"TS{max(existing_ids, default=0) + 1:02d}"
        
        spot_data['id'] = new_id
        spot_data['type'] = 'tourist_spot'
        self.tourist_spots.append(spot_data)
        return spot_data
    
    def add_cuisine(self, cuisine_data: Dict) -> Dict:
        """Add new cuisine"""
        # Generate new ID
        existing_ids = [int(c['id'][2:]) for c in self.cuisines if c['id'].startswith('CU')]
        new_id = f"CU{max(existing_ids, default=0) + 1:02d}"
        
        cuisine_data['id'] = new_id
        cuisine_data['type'] = 'cuisine'
        self.cuisines.append(cuisine_data)
        return cuisine_data
    
    def update_tourist_spot(self, spot_id: str, update_data: Dict) -> Optional[Dict]:
        """Update tourist spot"""
        for i, spot in enumerate(self.tourist_spots):
            if spot['id'] == spot_id:
                self.tourist_spots[i].update({k: v for k, v in update_data.items() if v is not None})
                return self.tourist_spots[i]
        return None
    
    def update_cuisine(self, cuisine_id: str, update_data: Dict) -> Optional[Dict]:
        """Update cuisine"""
        for i, cuisine in enumerate(self.cuisines):
            if cuisine['id'] == cuisine_id:
                self.cuisines[i].update({k: v for k, v in update_data.items() if v is not None})
                return self.cuisines[i]
        return None
    
    def delete_tourist_spot(self, spot_id: str) -> bool:
        """Delete tourist spot"""
        for i, spot in enumerate(self.tourist_spots):
            if spot['id'] == spot_id:
                self.tourist_spots.pop(i)
                return True
        return False
    
    def delete_cuisine(self, cuisine_id: str) -> bool:
        """Delete cuisine"""
        for i, cuisine in enumerate(self.cuisines):
            if cuisine['id'] == cuisine_id:
                self.cuisines.pop(i)
                return True
        return False

# Global instance
data_loader = DataLoader()