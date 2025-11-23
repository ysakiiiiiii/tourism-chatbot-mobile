from pyswip import Prolog
from app.config import PROLOG_KB
import pandas as pd
from app.config import EXCEL_FILE

class PrologService:
    def __init__(self):
        self.prolog = Prolog()
        self.excel_df = None
        self.load_kb()
        self.load_excel()
    
    def load_kb(self):
        """Load Prolog knowledge base"""
        try:
            self.prolog.consult(str(PROLOG_KB))
            print(f"✓ Prolog KB loaded from {PROLOG_KB}")
        except Exception as e:
            print(f"✗ Error loading Prolog KB: {e}")
            raise
    
    def load_excel(self):
        """Load Excel data for detail retrieval"""
        try:
            self.excel_df = pd.read_excel(EXCEL_FILE)
            print(f"✓ Excel data loaded: {len(self.excel_df)} records")
        except Exception as e:
            print(f"✗ Error loading Excel: {e}")
            raise
    
    def sanitize_query(self, text):
        """Sanitize user input for Prolog query"""
        text = text.lower().strip()
        # Remove quotes and escape special characters
        text = text.replace("'", "").replace('"', '')
        return text
    
    def query_by_keywords(self, keywords):
        """Query items by keywords"""
        results = set()
        for keyword in keywords:
            keyword = self.sanitize_query(keyword)
            try:
                # Try exact match first
                query = f"find_by_keyword('{keyword}', ID)"
                for solution in self.prolog.query(query):
                    results.add(solution['ID'])
                
                # Try partial match in item names
                query = f"find_by_name('{keyword}', ID)"
                for solution in self.prolog.query(query):
                    results.add(solution['ID'])
            except Exception as e:
                print(f"Query error for keyword '{keyword}': {e}")
        
        return list(results)
    
    def query_by_type(self, item_type):
        """Query items by type"""
        item_type = self.sanitize_query(item_type)
        results = []
        try:
            query = f"find_by_type('{item_type}', ID)"
            for solution in self.prolog.query(query):
                results.append(solution['ID'])
        except Exception as e:
            print(f"Query error for type '{item_type}': {e}")
        
        return results
    
    def query_by_location(self, location):
        """Query items by location"""
        location = self.sanitize_query(location)
        results = []
        try:
            query = f"find_by_location('{location}', ID)"
            for solution in self.prolog.query(query):
                results.append(solution['ID'])
        except Exception as e:
            print(f"Query error for location '{location}': {e}")
        
        return results
    
    def get_item_from_excel(self, item_id):
        """Get full item details from Excel by ID"""
        if self.excel_df is None:
            return None
        
        # Clean the item_id (remove quotes if present)
        item_id = str(item_id).strip("'\"")
        
        # Find the item in Excel
        item = self.excel_df[self.excel_df['id'] == item_id]
        
        if item.empty:
            return None
        
        # Convert to dict
        item_dict = item.iloc[0].to_dict()
        
        # Handle NaN values
        for key, value in item_dict.items():
            if pd.isna(value):
                item_dict[key] = None
        
        return item_dict
    
    def search(self, query_text, top_n=1):
        """
        Main search function that processes natural language query
        Uses NLP processing for better results
        
        Args:
            query_text: Natural language query
            top_n: Number of top results to return (default: 1)
        
        Returns:
            List of matching items with full details, ranked by relevance
        """
        from app.services.nlp_processor import get_nlp_processor
        
        # Get NLP processor
        nlp = get_nlp_processor()
        
        # Process query with NLP pipeline
        keywords = nlp.process_query(query_text)
        
        print(f"Original query: {query_text}")
        print(f"Processed keywords: {keywords}")
        
        if not keywords:
            return []
        
        # Search by processed keywords
        matched_ids = self.query_by_keywords(keywords)
        
        # Also search in names and locations using stemmed keywords
        for keyword in keywords:
            stemmed = nlp.stem_word(keyword)
            # Search in item names
            try:
                query = f"find_by_name('{stemmed}', ID)"
                for solution in self.prolog.query(query):
                    matched_ids.append(solution['ID'])
            except:
                pass
            
            # Search in locations
            try:
                query = f"find_by_location('{stemmed}', ID)"
                for solution in self.prolog.query(query):
                    matched_ids.append(solution['ID'])
            except:
                pass
        
        # Remove duplicates
        matched_ids = list(set(matched_ids))
        
        # Get full details from Excel
        items = []
        for item_id in matched_ids:
            details = self.get_item_from_excel(item_id)
            if details:
                items.append(details)
        
        # If no results from Prolog, try direct search in Excel
        if not items:
            print("No Prolog matches, searching directly in Excel...")
            items = self.search_in_excel(keywords)
        
        # Rank results by relevance
        ranked = nlp.rank_results(items, keywords, top_n=top_n)
        
        # Return just the items (without scores)
        results = [item for item, score, matched in ranked]
        
        if results:
            print(f"Top {len(results)} result(s) returned")
            for i, (item, score, matched) in enumerate(ranked[:len(results)], 1):
                print(f"  {i}. {item['name']} (score: {score}, matched: {', '.join(matched)})")
        
        return results
    
    def search_in_excel(self, keywords):
        """
        Direct search in Excel when Prolog doesn't find results
        Searches in name, location, description keywords, and full description
        """
        from app.services.nlp_processor import get_nlp_processor
        
        if self.excel_df is None:
            return []
        
        nlp = get_nlp_processor()
        results = []
        
        for _, row in self.excel_df.iterrows():
            # Get all searchable fields
            name = str(row.get('name', '')).lower()
            location = str(row.get('location', '')).lower()
            desc_kw = str(row.get('description_keywords', '')).lower()
            full_desc = str(row.get('full_description', '')).lower()
            
            # Combine all text
            combined = f"{name} {location} {desc_kw} {full_desc}"
            
            # Stem the combined text
            combined_stemmed = ' '.join([nlp.stem_word(w) for w in nlp.tokenize(combined)])
            
            # Check if any keyword matches
            for keyword in keywords:
                keyword_stemmed = nlp.stem_word(keyword)
                if keyword_stemmed in combined_stemmed:
                    item_dict = row.to_dict()
                    # Handle NaN values
                    for key, value in item_dict.items():
                        if pd.isna(value):
                            item_dict[key] = None
                    results.append(item_dict)
                    break  # Don't add the same item multiple times
        
        return results

# Singleton instance
_prolog_service = None

def get_prolog_service():
    global _prolog_service
    if _prolog_service is None:
        _prolog_service = PrologService()
    return _prolog_service