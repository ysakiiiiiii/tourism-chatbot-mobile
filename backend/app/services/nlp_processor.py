"""
NLP Processing for chatbot queries
Includes: tokenization, stop word removal, stemming, ranking, and location detection
"""
import re
from collections import Counter

class SimpleNLPProcessor:
    """
    Simple NLP processor without external dependencies
    Uses Porter Stemmer algorithm and custom stop words
    """
    
    def __init__(self):
        # Common English stop words
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
            'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
            'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
            'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
            'can', 'will', 'just', 'don', 'should', 'now',
            # Chatbot-specific stop words
            'want', 'find', 'search', 'show', 'tell', 'get', 'give', 'see',
            'looking', 'look', 'need', 'like', 'would', 'could', 'please'
        }
        
        # Common Ilocos locations - add more as needed
        self.known_locations = {
            'vigan', 'laoag', 'pagudpud', 'ilocos sur', 'ilocos norte',
            'batac', 'paoay', 'bangui', 'bacarra', 'burgos', 'pasuquin',
            'santa', 'caoayan', 'narvacan', 'candon', 'tagudin'
        }
        
        # Location indicator phrases
        self.location_indicators = [
            'in', 'at', 'near', 'around', 'from', 'located in', 
            'located at', 'found in', 'situated in'
        ]
        
        # Common word endings to remove (simple stemming)
        self.suffix_rules = [
            ('sses', 'ss'),
            ('ies', 'i'),
            ('ss', 'ss'),
            ('s', ''),
            ('ed', ''),
            ('ing', ''),
            ('ly', ''),
            ('ful', ''),
        ]
    
    def detect_location(self, text):
        """
        Detect if user specifies a location in their query
        Returns: location string or None
        """
        text_lower = text.lower()
        
        # Check for known locations
        for location in self.known_locations:
            # Direct match
            if location in text_lower:
                return location
            
            # Check with location indicators
            for indicator in self.location_indicators:
                pattern = f"{indicator}\\s+{location}"
                if re.search(pattern, text_lower):
                    return location
        
        return None
    
    def stem_word(self, word):
        """Simple stemming using suffix removal"""
        word = word.lower()
        
        # Special cases for common words
        special_cases = {
            'beaches': 'beach',
            'churches': 'church',
            'dishes': 'dish',
            'places': 'place',
            'foods': 'food',
            'spots': 'spot',
            'rocks': 'rock',
            'caves': 'cave',
            'fried': 'fry',
            'grilled': 'grill',
            'stuffed': 'stuff',
            'cooked': 'cook',
        }
        
        if word in special_cases:
            return special_cases[word]
        
        # Apply suffix rules
        for suffix, replacement in self.suffix_rules:
            if word.endswith(suffix):
                word = word[:-len(suffix)] + replacement
                break
        
        return word
    
    def tokenize(self, text):
        """Tokenize text into words, remove punctuation"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return words
    
    def remove_stop_words(self, words):
        """Remove common stop words"""
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def process_query(self, query):
        """
        Full NLP pipeline:
        1. Detect location (if specified)
        2. Tokenize
        3. Remove stop words
        4. Stem words
        
        Returns: (keywords, detected_location)
        """
        # Detect location first
        detected_location = self.detect_location(query)
        
        # Tokenize
        tokens = self.tokenize(query)
        
        # Remove stop words (but keep location if detected)
        filtered = self.remove_stop_words(tokens)
        
        # Stem words
        stemmed = [self.stem_word(word) for word in filtered]
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for word in stemmed:
            if word not in seen:
                seen.add(word)
                result.append(word)
        
        return result, detected_location
    
    def calculate_relevance_score(self, item, keywords, location_filter=None):
        """
        Calculate relevance score for an item based on keyword matches
        
        Args:
            item: Item dictionary
            keywords: List of keywords to match
            location_filter: Optional location to filter by
        
        Returns:
            (score, matched_keywords)
        """
        score = 0
        matched_keywords = []
        unique_matches = set()
        
        # Get item fields
        name = str(item.get('name', '')).lower()
        location = str(item.get('location', '')).lower()
        desc_keywords = str(item.get('description_keywords', '')).lower()
        full_desc = str(item.get('full_description', '')).lower()
        
        # LOCATION FILTER: If user specified a location, check if item matches
        if location_filter:
            location_filter_lower = location_filter.lower()
            if location_filter_lower not in location:
                # Item doesn't match the specified location - heavily penalize or skip
                return 0, []  # Return 0 score to effectively filter it out
        
        # Stem the item fields
        name_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(name)])
        location_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(location)])
        desc_keywords_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(desc_keywords)])
        full_desc_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(full_desc)])
        
        for keyword in keywords:
            keyword_stemmed = self.stem_word(keyword)
            keyword_matched = False
            
            # Check name (highest priority)
            if keyword_stemmed in name_stemmed:
                if keyword_stemmed == name_stemmed:
                    score += 10
                    matched_keywords.append(f"name:{keyword}")
                else:
                    score += 5
                    matched_keywords.append(f"name:{keyword}")
                keyword_matched = True
            
            # Check location
            if keyword_stemmed in location_stemmed:
                score += 3
                matched_keywords.append(f"location:{keyword}")
                keyword_matched = True
            
            # Check description keywords
            if keyword_stemmed in desc_keywords_stemmed:
                desc_kw_list = [kw.strip().lower() for kw in desc_keywords.split(',')]
                if keyword.lower() in desc_kw_list or keyword_stemmed in desc_kw_list:
                    score += 3
                else:
                    score += 2
                matched_keywords.append(f"desc:{keyword}")
                keyword_matched = True
            
            # Check full description
            elif keyword_stemmed in full_desc_stemmed:
                score += 1
                matched_keywords.append(f"full_desc:{keyword}")
                keyword_matched = True
            
            if keyword_matched:
                unique_matches.add(keyword_stemmed)
        
        # Multiple keyword matches bonus
        if len(unique_matches) > 1:
            bonus = (len(unique_matches) - 1) * 5
            score += bonus
            matched_keywords.append(f"multi_match_bonus:{bonus}")
        
        # BONUS: If location_filter is specified and matched, give extra points
        if location_filter and location_filter.lower() in location:
            score += 8  # Significant bonus for matching the specified location
            matched_keywords.append(f"location_filter_match:{location_filter}")
        
        return score, matched_keywords
    
    def rank_results(self, items, keywords, location_filter=None, top_n=1):
        """
        Rank items by relevance score and return top N
        
        Args:
            items: List of item dictionaries
            keywords: List of processed keywords
            location_filter: Optional location to filter by
            top_n: Number of top results to return
        
        Returns:
            List of tuples: (item, score, matched_keywords)
        """
        scored_items = []
        
        for item in items:
            score, matched = self.calculate_relevance_score(item, keywords, location_filter)
            if score > 0:
                scored_items.append((item, score, matched))
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        return scored_items[:top_n]

# Singleton instance
_nlp_processor = None

def get_nlp_processor():
    """Get or create NLP processor singleton"""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = SimpleNLPProcessor()
    return _nlp_processor