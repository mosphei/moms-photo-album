from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

# Schema for a single person (used for reading data)
class PersonSchema(BaseModel):
    id: int
    name: str
    past_names: Optional[str] = None

    class Config:
        # Allows Pydantic to read ORM objects directly
        from_attributes = True

# Schema for creating a new person (no ID needed yet)
class PersonCreate(BaseModel):
    name: str
    past_names: Optional[str] = None

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    past_names: Optional[str] = None

# Schema for a single image (used for reading data)
class PhotoSchema(BaseModel):
    id: int
    filename: str
    date_taken: datetime
    date_uploaded: datetime
    date_updated: datetime
    description: Optional[str] = None
    # Nested Pydantic model to list people in the image
    people: List[PersonSchema] = []

    class Config:
        from_attributes = True

# Schema for creating a new image (ID handled by DB, provide file path and optional people IDs)
class PhotoCreate(BaseModel):
    user_id: int
    file_path: str
    filename: str
    date_taken: datetime | None = None
    hash: str
    md5sum: str

# Schema for partial updates
class PhotoUpdate(BaseModel):
    filename: Optional[str] = None
    date_taken: Optional[datetime] = None
    date_uploaded: Optional[datetime] = None
    description: Optional[str] = None
    # Nested Pydantic model to list people in the image
    people: Optional[List[PersonSchema]] = None
    rotation: Optional[int] = None

    class Config:
        # Allows Pydantic to read ORM objects directly
        from_attributes = True
        
class UserCreate(BaseModel):
    username: str
    password: str
    person: PersonSchema

class UserAuthenticate(BaseModel):
    username: str
    password: str
    hashed_password: str

class UserSchema(BaseModel):
    id: int 
    username: str
    person: PersonSchema | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None