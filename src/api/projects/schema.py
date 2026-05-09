from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class PlaceImport(BaseModel):
    external_id: int = Field(..., description="Artwork ID from Art Institute of Chicago API")


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[date] = None
    places: Optional[List[PlaceImport]] = Field(
        default=None, description="Optional initial places (1-10)"
    )

    @field_validator("places")
    @classmethod
    def validate_places_count(cls, v):
        if v is not None:
            if len(v) < 1:
                raise ValueError("At least 1 place required when providing places")
            if len(v) > 10:
                raise ValueError("Maximum 10 places per project")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[date] = None


class ProjectResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    places: List = []

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    is_completed: bool
    place_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedProjects(BaseModel):
    items: List[ProjectListItem]
    total: int
    page: int
    size: int
    pages: int
