"""
NLP Processing for chatbot queries
Includes: tokenization, stop word removal, stemming, and ranking
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
        
        # Common word endings to remove (simple stemming)
        self.suffix_rules = [
            ('sses', 'ss'),  # processes -> process
            ('ies', 'i'),    # ponies -> poni
            ('ss', 'ss'),    # stress -> stress
            ('s', ''),       # cats -> cat
            ('ed', ''),      # played -> play
            ('ing', ''),     # playing -> play
            ('ly', ''),      # quickly -> quick
            ('ful', ''),     # beautiful -> beauti
        ]
    
    def stem_word(self, word):
        """
        Simple stemming using suffix removal
        """
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
        """
        Tokenize text into words, remove punctuation
        """
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        return words
    
    def remove_stop_words(self, words):
        """
        Remove common stop words
        """
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def process_query(self, query):
        """
        Full NLP pipeline:
        1. Tokenize
        2. Remove stop words
        3. Stem words
        
        Returns list of processed keywords
        """
        # Tokenize
        tokens = self.tokenize(query)
        
        # Remove stop words
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
        
        return result
    
    def calculate_relevance_score(self, item, keywords):
        """
        Calculate relevance score for an item based on keyword matches
        Higher score = more relevant
        
        Scoring weights:
        - Name exact match: 10 points
        - Name contains keyword: 5 points
        - Location match: 3 points
        - Description keyword exact match: 2 points
        - Description keyword partial match: 1 point
        """
        score = 0
        matched_keywords = []
        
        # Get item fields
        name = str(item.get('name', '')).lower()
        location = str(item.get('location', '')).lower()
        desc_keywords = str(item.get('description_keywords', '')).lower()
        full_desc = str(item.get('full_description', '')).lower()
        
        # Stem the item fields
        name_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(name)])
        location_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(location)])
        desc_keywords_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(desc_keywords)])
        full_desc_stemmed = ' '.join([self.stem_word(w) for w in self.tokenize(full_desc)])
        
        for keyword in keywords:
            keyword_stemmed = self.stem_word(keyword)
            
            # Check name (highest priority)
            if keyword_stemmed in name_stemmed:
                if keyword_stemmed == name_stemmed:
                    score += 10  # Exact match
                    matched_keywords.append(f"name:{keyword}")
                else:
                    score += 5  # Partial match
                    matched_keywords.append(f"name:{keyword}")
            
            # Check location
            if keyword_stemmed in location_stemmed:
                score += 3
                matched_keywords.append(f"location:{keyword}")
            
            # Check description keywords (medium priority)
            if keyword_stemmed in desc_keywords_stemmed:
                # Check if exact match in original keywords
                if keyword in desc_keywords.split(','):
                    score += 2
                else:
                    score += 1.5
                matched_keywords.append(f"desc:{keyword}")
            
            # Check full description (lower priority)
            if keyword_stemmed in full_desc_stemmed:
                score += 1
                matched_keywords.append(f"full_desc:{keyword}")
        
        return score, matched_keywords
    
    def rank_results(self, items, keywords, top_n=1):
        """
        Rank items by relevance score and return top N
        
        Args:
            items: List of item dictionaries
            keywords: List of processed keywords
            top_n: Number of top results to return (default: 1)
        
        Returns:
            List of tuples: (item, score, matched_keywords)
        """
        scored_items = []
        
        for item in items:
            score, matched = self.calculate_relevance_score(item, keywords)
            if score > 0:  # Only include items with at least one match
                scored_items.append((item, score, matched))
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N
        return scored_items[:top_n]

# Singleton instance
_nlp_processor = None

def get_nlp_processor():
    """Get or create NLP processor singleton"""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = SimpleNLPProcessor()
    return _nlp_processor