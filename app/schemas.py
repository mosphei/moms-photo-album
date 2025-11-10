from typing import List, Optional
from pydantic import BaseModel, HttpUrl

# Schema for a single person (used for reading data)
class PersonSchema(BaseModel):
    id: int
    name: str

    class Config:
        # Allows Pydantic to read ORM objects directly
        from_attributes = True

# Schema for creating a new person (no ID needed yet)
class PersonCreate(BaseModel):
    name: str

# Schema for a single image (used for reading data)
class ImageSchema(BaseModel):
    id: int
    file_path: str
    description: Optional[str] = None
    # Nested Pydantic model to list people in the image
    people: List[PersonSchema] = []

    class Config:
        from_attributes = True

# Schema for creating a new image (ID handled by DB, provide file path and optional people IDs)
class ImageCreate(BaseModel):
    file_path: str
    description: Optional[str] = None
    person_ids: List[int] = []
