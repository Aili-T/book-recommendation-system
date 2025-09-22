from dataclasses import dataclass

@dataclass(frozen=True)
class Book:
    id: str
    title: str
    author: str
    genre: str
    year: int
    rating: float

@dataclass(frozen=True)
class User:
    id: str
    name: str

@dataclass(frozen=True)
class Rating:
    user_id: str
    book_id: str
    value: int