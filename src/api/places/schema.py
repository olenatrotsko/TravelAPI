from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectPlaceCreate(BaseModel):
    external_id: int = Field(..., description="Artwork ID from Art Institute of Chicago API")


class ProjectPlaceUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=5000)
    is_visited: Optional[bool] = None


class ProjectPlaceResponse(BaseModel):
    id: int
    project_id: int
    external_id: int
    title: str
    artist_display: Optional[str]
    place_of_origin: Optional[str]
    image_url: Optional[str]
    notes: Optional[str]
    is_visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
