from typing import TypeVar, Generic, List

# Define a Type Variable (T is a common convention)
T = TypeVar('T')

# Define the generic class, inheriting from Generic[T]
class PaginatedResults(Generic[T]):
    def __init__(self, items: List[T], total_count: int, offset: int, limit: int):
        self.items: List[T] = items
        self.total_count: int = total_count
        self.offset: int = offset
        self.limit: int = limit
    
    def __repr__(self):
        return f"<PaginatedResults total={self.total_count} items={len(self.items)}>"
