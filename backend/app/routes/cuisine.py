from fastapi import APIRouter, HTTPException
from app.models.schemas import Cuisine, CuisineCreate, CuisineUpdate
import pandas as pd
from app.config import EXCEL_FILE
from app.services.excel_to_prolog import convert_excel_to_prolog
from app.services.prolog_service import get_prolog_service

router = APIRouter(prefix="/api/cuisine", tags=["Cuisine"])

def load_excel():
    """Load Excel data"""
    return pd.read_excel(EXCEL_FILE)

def save_excel(df):
    """Save Excel data and regenerate Prolog KB"""
    df.to_excel(EXCEL_FILE, index=False)
    convert_excel_to_prolog()
    # Reload Prolog service
    get_prolog_service().load_kb()
    get_prolog_service().load_excel()

@router.get("/", response_model=list[Cuisine])
async def get_all_cuisine():
    """Get all cuisine items"""
    try:
        df = load_excel()
        cuisine_df = df[df['type'] == 'cuisine']
        # Replace NaN with None
        cuisine_df = cuisine_df.where(pd.notna(cuisine_df), None)
        cuisine = cuisine_df.to_dict('records')
        return cuisine
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cuisine_id}", response_model=Cuisine)
async def get_cuisine(cuisine_id: str):
    """Get a specific cuisine by ID"""
    try:
        df = load_excel()
        cuisine = df[df['id'] == cuisine_id]
        
        if cuisine.empty:
            raise HTTPException(status_code=404, detail="Cuisine not found")
        
        # Replace NaN with None
        cuisine_dict = cuisine.iloc[0].to_dict()
        for key, value in cuisine_dict.items():
            if pd.isna(value):
                cuisine_dict[key] = None
        
        return cuisine_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Cuisine)
async def create_cuisine(cuisine: CuisineCreate):
    """Create a new cuisine item"""
    try:
        df = load_excel()
        
        # Check if ID already exists
        if cuisine.id in df['id'].values:
            raise HTTPException(status_code=400, detail="ID already exists")
        
        # Add new row
        new_row = cuisine.model_dump()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save and regenerate KB
        save_excel(df)
        
        return cuisine
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cuisine_id}", response_model=Cuisine)
async def update_cuisine(cuisine_id: str, cuisine_update: CuisineUpdate):
    """Update a cuisine item"""
    try:
        df = load_excel()
        
        # Find the cuisine
        idx = df[df['id'] == cuisine_id].index
        
        if len(idx) == 0:
            raise HTTPException(status_code=404, detail="Cuisine not found")
        
        # Update fields
        update_data = cuisine_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            df.at[idx[0], key] = value
        
        # Save and regenerate KB
        save_excel(df)
        
        # Return updated record with NaN handling
        result_dict = df.iloc[idx[0]].to_dict()
        for key, value in result_dict.items():
            if pd.isna(value):
                result_dict[key] = None
        
        return result_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{cuisine_id}")
async def delete_cuisine(cuisine_id: str):
    """Delete a cuisine item"""
    try:
        df = load_excel()
        
        # Check if exists
        if cuisine_id not in df['id'].values:
            raise HTTPException(status_code=404, detail="Cuisine not found")
        
        # Delete row
        df = df[df['id'] != cuisine_id]
        
        # Save and regenerate KB
        save_excel(df)
        
        return {"message": f"Cuisine {cuisine_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))