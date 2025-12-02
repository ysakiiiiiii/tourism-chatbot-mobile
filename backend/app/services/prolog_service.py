from pyswip import Prolog
from app.config import PROLOG_KB
import pandas as pd
from app.config import EXCEL_FILE
from app.services.conversation_context import get_conversation_manager
import os

class ContextAwarePrologService:
    def __init__(self):
        try:
            self.prolog = Prolog()
        except Exception as e:
            print(f"⚠ Warning: PySwip initialization issue: {e}")
            print("  This may be due to SWI-Prolog version incompatibility.")
            print("  Recommended: Downgrade SWI-Prolog to version 8.4.3")
            raise
        
        self.excel_df = None
        self.conversation_manager = get_conversation_manager()
        
        # Photo base path configuration
        # This should match your frontend's public folder structure
        # Example: If photos are in frontend/public/assets/bagnet.jpg
        # Then PHOTO_BASE_PATH should be "assets"
        self.PHOTO_BASE_PATH = "assets"
        
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
    
    def build_photo_url(self, photo_filename):
        """
        Build photo URL from filename
        Returns None if photo_filename is empty/null
        Automatically adds .jpg extension if missing
        """
        if not photo_filename or pd.isna(photo_filename):
            return None
        
        # Remove any leading/trailing whitespace
        photo_filename = str(photo_filename).strip()
        
        if not photo_filename:
            return None
        
        # Check if filename already has an extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        has_extension = any(photo_filename.lower().endswith(ext) for ext in valid_extensions)
        
        # Add .jpg extension if missing
        if not has_extension:
            photo_filename = f"{photo_filename}.jpg"
        
        # Build the full path
        # Format: assets/bagnet.jpg
        return f"{self.PHOTO_BASE_PATH}/{photo_filename}"
    
    def sanitize_query(self, text):
        """Sanitize user input for Prolog query"""
        text = text.lower().strip()
        text = text.replace("'", "").replace('"', '')
        return text
    
    def query_by_keywords(self, keywords):
        """Query items by keywords"""
        results = set()
        for keyword in keywords:
            keyword = self.sanitize_query(keyword)
            try:
                query = f"find_by_keyword('{keyword}', ID)"
                for solution in self.prolog.query(query):
                    results.add(solution['ID'])
                
                query = f"find_by_name('{keyword}', ID)"
                for solution in self.prolog.query(query):
                    results.add(solution['ID'])
            except Exception as e:
                print(f"Query error for keyword '{keyword}': {e}")
        
        return list(results)
    
    def get_item_from_excel(self, item_id):
        """Get full item details from Excel by ID, including photo URL"""
        if self.excel_df is None:
            return None
        
        item_id = str(item_id).strip("'\"")
        item = self.excel_df[self.excel_df['id'] == item_id]
        
        if item.empty:
            return None
        
        item_dict = item.iloc[0].to_dict()
        
        # Handle NaN values
        for key, value in item_dict.items():
            if pd.isna(value):
                item_dict[key] = None
        
        # Build photo URL
        photo_filename = item_dict.get('photo')
        item_dict['photo_url'] = self.build_photo_url(photo_filename)
        
        return item_dict
    
    def search_with_context(self, query_text: str, session_id: str, top_n: int = 1):
        """
        Context-aware search that considers conversation history and location
        
        Args:
            query_text: User's current query
            session_id: Session ID for conversation tracking
            top_n: Number of results to return
        
        Returns:
            List of matching items (with photo_url), conversation context
        """
        from app.services.nlp_processor import get_nlp_processor
        
        # Get or create conversation context
        context = self.conversation_manager.get_or_create_session(session_id)
        
        # Get NLP processor
        nlp = get_nlp_processor()
        
        # Process current query with location detection
        keywords, detected_location = nlp.process_query(query_text)
        
        print(f"\n{'='*60}")
        print(f"Session: {session_id} (Turn {context.turn_count + 1})")
        print(f"Query: {query_text}")
        print(f"Processed keywords: {keywords}")
        print(f"Detected location: {detected_location}")
        
        # Detect if user is explicitly asking for alternatives
        asking_alternatives = self._is_asking_for_alternatives(query_text)
        
        # Check if this is a follow-up query (including explicit alternatives requests)
        is_followup = context.is_followup_query(query_text) or asking_alternatives
        print(f"Is follow-up: {is_followup} (asking_alternatives={asking_alternatives})")
        
        # Enhance keywords with context if it's a follow-up
        enhanced_keywords = keywords.copy()
        if is_followup and context.last_keywords:
            context_keywords = context.get_context_keywords()
            
            for ctx_kw in context_keywords:
                if ctx_kw not in enhanced_keywords:
                    enhanced_keywords.append(ctx_kw)
            
            print(f"Enhanced with context: {enhanced_keywords}")
        
        # Search using enhanced keywords
        matched_ids = self.query_by_keywords(enhanced_keywords)
        # Additional searches with stemming
        for keyword in enhanced_keywords:
            stemmed = nlp.stem_word(keyword)
            try:
                query = f"find_by_name('{stemmed}', ID)"
                for solution in self.prolog.query(query):
                    matched_ids.append(solution['ID'])
            except:
                pass
            
            try:
                query = f"find_by_location('{stemmed}', ID)"
                for solution in self.prolog.query(query):
                    matched_ids.append(solution['ID'])
            except:
                pass
        
        # Remove duplicates
        matched_ids = list(set(matched_ids))
        
        # Get full details from Excel (now includes photo_url)
        items = []
        for item_id in matched_ids:
            details = self.get_item_from_excel(item_id)
            if details:
                items.append(details)
        
        # If no results from Prolog, search directly in Excel
        if not items:
            print("No Prolog matches, searching directly in Excel...")
            items = self.search_in_excel(enhanced_keywords)
        
        # Handle alternatives follow-up: restrict to same location/type as last item,
        # prefer items not shown in the last turn, otherwise exclude all previously mentioned items.
        # Shuffle to avoid repeatedly returning the same top-ranked item.
        if asking_alternatives:
            original_count = len(items)
            
            # Get location and type constraints from the last item
            last_location = None
            last_type = None
            if context.last_items:
                try:
                    last_location = context.last_items[0].get('location', '').lower().strip()
                    last_type = context.last_items[0].get('type', '').lower().strip()
                    print(f"Restricting alternatives to location='{last_location}', type='{last_type}'")
                except:
                    pass
            
            # Filter items to match location and type of the last result
            if last_location or last_type:
                filtered_by_context = []
                for item in items:
                    item_location = item.get('location', '').lower().strip()
                    item_type = item.get('type', '').lower().strip()
                    
                    # Match if same location OR same type
                    location_match = last_location and last_location in item_location
                    type_match = last_type and last_type in item_type
                    
                    if location_match or type_match:
                        filtered_by_context.append(item)
                
                if filtered_by_context:
                    items = filtered_by_context
                    print(f"Filtered to context-matching items; {len(items)} candidate(s) remain")
                else:
                    print(f"No items match location/type context; keeping all {len(items)} for filtering by history")
            
            # Try to remove only the items shown in the last bot response first
            try:
                last_ids = {it.get('id') for it in context.last_items if it and isinstance(it, dict)}
            except Exception:
                last_ids = set()

            # Items that were NOT in the last turn
            unseen_since_last = [item for item in items if item.get('id') not in last_ids]

            if unseen_since_last:
                items = unseen_since_last
                print(f"Excluding last-turn items; {len(items)} candidate(s) remain")
                context.last_alternatives_exhausted = False
            else:
                # Fallback: exclude any item mentioned previously in the session
                items = [item for item in items if item.get('id') not in context.mentioned_items]
                print(f"Excluded all previously mentioned items; {len(items)} candidate(s) remain")

                # If still nothing unseen, mark alternatives exhausted so UI/response
                # can inform the user there are no more different options
                if not items:
                    context.last_alternatives_exhausted = True
                else:
                    context.last_alternatives_exhausted = False

            # Shuffle remaining items so the same top-ranked item isn't always returned
            import random
            if items:
                random.shuffle(items)

            print(f"Filtered out {original_count - len(items)} previously shown items")
        
        # Rank results by relevance WITH LOCATION FILTER
        ranked = nlp.rank_results(items, keywords, location_filter=detected_location, top_n=top_n)
        
        # Extract just the items
        results = [item for item, score, matched in ranked]
        
        # Log results
        if results:
            print(f"\nTop {len(results)} result(s):")
            for i, (item, score, matched) in enumerate(ranked[:len(results)], 1):
                photo_status = "✓ Has photo" if item.get('photo_url') else "✗ No photo"
                print(f"  {i}. {item['name']} (score: {score}) [{photo_status}]")
        else:
            print("No results found")
        
        if detected_location and not results:
            print(f"⚠ No results found for location: {detected_location}")
        
        print(f"{'='*60}\n")
        
        return results, context
    
    def _is_asking_for_alternatives(self, query: str) -> bool:
        """Check if user is asking for alternative/different options"""
        alternative_phrases = [
            'another', 'different', 'alternative', 'else', 'other',
            'more options', 'something else', 'besides', 'instead'
        ]
        query_lower = query.lower()
        return any(phrase in query_lower for phrase in alternative_phrases)
    
    def search_in_excel(self, keywords):
        """Direct search in Excel when Prolog doesn't find results"""
        from app.services.nlp_processor import get_nlp_processor
        
        if self.excel_df is None:
            return []
        
        nlp = get_nlp_processor()
        results = []
        
        for _, row in self.excel_df.iterrows():
            name = str(row.get('name', '')).lower()
            location = str(row.get('location', '')).lower()
            desc_kw = str(row.get('description_keywords', '')).lower()
            full_desc = str(row.get('full_description', '')).lower()
            
            combined = f"{name} {location} {desc_kw} {full_desc}"
            combined_stemmed = ' '.join([nlp.stem_word(w) for w in nlp.tokenize(combined)])
            
            for keyword in keywords:
                keyword_stemmed = nlp.stem_word(keyword)
                if keyword_stemmed in combined_stemmed:
                    item_dict = row.to_dict()
                    
                    # Handle NaN values
                    for key, value in item_dict.items():
                        if pd.isna(value):
                            item_dict[key] = None
                    
                    # Build photo URL
                    photo_filename = item_dict.get('photo')
                    item_dict['photo_url'] = self.build_photo_url(photo_filename)
                    
                    results.append(item_dict)
                    break
        
        return results
    
    def update_conversation_context(self, session_id: str, query: str, 
                                   keywords: list, response: str, items: list):
        """Update conversation context after generating response"""
        context = self.conversation_manager.get_or_create_session(session_id)
        context.add_turn(query, keywords, response, items)
    
    def reset_conversation(self, session_id: str):
        """Reset conversation for a session"""
        self.conversation_manager.reset_session(session_id)
    
    def get_conversation_summary(self, session_id: str):
        """Get conversation summary for debugging"""
        context = self.conversation_manager.get_or_create_session(session_id)
        return context.get_summary()


# Singleton instance
_prolog_service = None

def get_prolog_service():
    global _prolog_service
    if _prolog_service is None:
        _prolog_service = ContextAwarePrologService()
    return _prolog_service