"""
Helper utility functions
"""
import pandas as pd

def clean_nan_values(data):
    """
    Replace pandas NaN values with None for proper JSON serialization
    """
    if isinstance(data, dict):
        return {k: None if pd.isna(v) else v for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    elif isinstance(data, pd.DataFrame):
        return data.where(pd.notna(data), None)
    else:
        return None if pd.isna(data) else data

def df_to_dict_clean(df, orient='records'):
    """
    Convert DataFrame to dict with NaN values replaced by None
    """
    if df.empty:
        return [] if orient == 'records' else {}
    df_clean = df.where(pd.notna(df), None)
    return df_clean.to_dict(orient)