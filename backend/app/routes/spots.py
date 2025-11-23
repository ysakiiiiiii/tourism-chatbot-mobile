from fastapi import APIRouter, HTTPException
from app.models.schemas import TouristSpot, TouristSpotCreate, TouristSpotUpdate
import pandas as pd
from app.config import EXCEL_FILE
from app.services.excel_to_prolog import convert_excel_to_prolog
from app.services.prolog_service import get_prolog_service

router = APIRouter(prefix="/api/spots", tags=["Tourist Spots"])

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

@router.get("/", response_model=list[TouristSpot])
async def get_all_spots():
    """Get all tourist spots"""
    try:
        df = load_excel()
        spots_df = df[df['type'] == 'tourist_spot']
        # Replace NaN with None
        spots_df = spots_df.where(pd.notna(spots_df), None)
        spots = spots_df.to_dict('records')
        return spots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{spot_id}", response_model=TouristSpot)
async def get_spot(spot_id: str):
    """Get a specific tourist spot by ID"""
    try:
        df = load_excel()
        spot = df[df['id'] == spot_id]
        
        if spot.empty:
            raise HTTPException(status_code=404, detail="Tourist spot not found")
        
        # Replace NaN with None
        spot_dict = spot.iloc[0].to_dict()
        for key, value in spot_dict.items():
            if pd.isna(value):
                spot_dict[key] = None
        
        return spot_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TouristSpot)
async def create_spot(spot: TouristSpotCreate):
    """Create a new tourist spot"""
    try:
        df = load_excel()
        
        # Check if ID already exists
        if spot.id in df['id'].values:
            raise HTTPException(status_code=400, detail="ID already exists")
        
        # Add new row
        new_row = spot.model_dump()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save and regenerate KB
        save_excel(df)
        
        return spot
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{spot_id}", response_model=TouristSpot)
async def update_spot(spot_id: str, spot_update: TouristSpotUpdate):
    """Update a tourist spot"""
    try:
        df = load_excel()
        
        # Find the spot
        idx = df[df['id'] == spot_id].index
        
        if len(idx) == 0:
            raise HTTPException(status_code=404, detail="Tourist spot not found")
        
        # Update fields
        update_data = spot_update.model_dump(exclude_unset=True)
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

@router.delete("/{spot_id}")
async def delete_spot(spot_id: str):
    """Delete a tourist spot"""
    try:
        df = load_excel()
        
        # Check if exists
        if spot_id not in df['id'].values:
            raise HTTPException(status_code=404, detail="Tourist spot not found")
        
        # Delete row
        df = df[df['id'] != spot_id]
        
        # Save and regenerate KB
        save_excel(df)
        
        return {"message": f"Tourist spot {spot_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))