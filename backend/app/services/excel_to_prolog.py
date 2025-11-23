import pandas as pd
from pathlib import Path
from app.config import EXCEL_FILE, PROLOG_KB

def sanitize_atom(text):
    """Convert text to a valid Prolog atom"""
    if pd.isna(text):
        return "'n/a'"
    
    text = str(text).strip()
    
    # Escape single quotes by doubling them (Prolog standard)
    text = text.replace("'", "''")
    
    # Always wrap in single quotes for safety
    # This handles all special characters including newlines, tabs, etc.
    return f"'{text}'"

def convert_excel_to_prolog():
    """Convert Excel data to Prolog knowledge base"""
    
    # Read Excel file
    df = pd.read_excel(EXCEL_FILE)
    
    # Create Prolog file
    prolog_content = []
    prolog_content.append("% Ilocos Tourism Knowledge Base")
    prolog_content.append("% Auto-generated from Excel data\n")
    
    # Add discontiguous directives to prevent warnings
    prolog_content.extend([
        "% Discontiguous directives",
        ":- discontiguous item/4.",
        ":- discontiguous has_keyword/2.",
        ":- discontiguous description/2.",
        ":- discontiguous best_time/2.",
        ":- discontiguous related/2.",
        ":- discontiguous nearest_hub/2.",
        ""
    ])
    
    # Process each row
    for _, row in df.iterrows():
        # Strip all values before sanitizing to remove leading/trailing spaces
        item_id = sanitize_atom(str(row['id']).strip() if pd.notna(row['id']) else row['id'])
        name = sanitize_atom(str(row['name']).strip() if pd.notna(row['name']) else row['name'])
        item_type = sanitize_atom(str(row['type']).strip() if pd.notna(row['type']) else row['type'])
        location = sanitize_atom(str(row['location']).strip() if pd.notna(row['location']) else row['location'])
        
        # Main fact
        prolog_content.append(
            f"item({item_id}, {name}, {item_type}, {location})."
        )
        
        # Description keywords as separate facts for better matching
        if pd.notna(row['description_keywords']):
            keywords = str(row['description_keywords']).split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    kw_atom = sanitize_atom(keyword)
                    prolog_content.append(
                        f"has_keyword({item_id}, {kw_atom})."
                    )
        
        # Full description
        full_desc = sanitize_atom(str(row['full_description']).strip() if pd.notna(row['full_description']) else row['full_description'])
        prolog_content.append(
            f"description({item_id}, {full_desc})."
        )
        
        # Best time to visit
        best_time = sanitize_atom(str(row['best_time_to_visit']).strip() if pd.notna(row['best_time_to_visit']) else row['best_time_to_visit'])
        prolog_content.append(
            f"best_time({item_id}, {best_time})."
        )
        
        # Related items
        if pd.notna(row['related_items']):
            related = str(row['related_items']).split(',')
            for rel in related:
                rel = rel.strip()
                if rel and rel.lower() != 'n/a':
                    rel_atom = sanitize_atom(rel)
                    prolog_content.append(
                        f"related({item_id}, {rel_atom})."
                    )
        
        # Nearest hub
        hub = sanitize_atom(str(row['nearest_hub']).strip() if pd.notna(row['nearest_hub']) else row['nearest_hub'])
        prolog_content.append(
            f"nearest_hub({item_id}, {hub})."
        )
        
        prolog_content.append("")  # Empty line for readability
    
    # Add query rules
    prolog_content.extend([
        "\n% Query Rules",
        "% Find items by keyword",
        "find_by_keyword(Keyword, ID) :-",
        "    has_keyword(ID, Keyword).",
        "",
        "% Find items by type",
        "find_by_type(Type, ID) :-",
        "    item(ID, _, Type, _).",
        "",
        "% Find items by location",
        "find_by_location(Location, ID) :-",
        "    item(ID, _, _, Location).",
        "",
        "% Find items by name (partial match)",
        "find_by_name(Name, ID) :-",
        "    item(ID, ItemName, _, _),",
        "    sub_atom(ItemName, _, _, _, Name).",
        "",
        "% Get full item details",
        "get_item_details(ID, Name, Type, Location, Desc, BestTime, Hub) :-",
        "    item(ID, Name, Type, Location),",
        "    description(ID, Desc),",
        "    best_time(ID, BestTime),",
        "    nearest_hub(ID, Hub).",
    ])
    
    # Write to file
    PROLOG_KB.parent.mkdir(parents=True, exist_ok=True)
    with open(PROLOG_KB, 'w', encoding='utf-8') as f:
        f.write('\n'.join(prolog_content))
    
    print(f"✓ Prolog KB generated at {PROLOG_KB}")
    print(f"✓ Processed {len(df)} items")
    
    return True

if __name__ == "__main__":
    convert_excel_to_prolog()