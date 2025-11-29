from typing import TypeVar, Generic, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

# Define a Type Variable (T is a common convention)
T = TypeVar('T')

# Define the generic class, inheriting from GenericModel and Generic[T]
class PaginatedResults(GenericModel, Generic[T]):
    items: List[T]
    total_count: int
    offset: int
    limit: int
    