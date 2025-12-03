from functools import reduce
from typing import Tuple
import json


def filter_books_by_year(books: Tuple, min_year: int) -> Tuple:
    """Filter by publication year"""
    return tuple(filter(lambda b: b.year >= min_year, books))
    #Filters books published after 2000 year

def filter_books_by_genre(books: Tuple, genre: str) -> Tuple:
    """Filter by genre"""
    return tuple(filter(lambda b: b.genre == genre, books))


def get_book_titles(books: Tuple) -> Tuple[str, ...]:
    """Extract book titles"""
    return tuple(map(lambda b: b.title, books))
     #Extracts titles

def get_average_rating(books: Tuple) -> float:
    """Calculate average rating"""
    if not books:
        return 0.0
    total = reduce(lambda acc, b: acc + b.rating, books, 0)
    return total / len(books)
     #Calculates the average rating

def add_rating(ratings: Tuple, new_rating) -> Tuple:
    """Add new rating"""
    return ratings + (new_rating,)


def avg_rating_for_book(ratings: Tuple, book_id: str) -> float:
    """Calculate average for a specific book"""
    book_ratings = tuple(r for r in ratings if r.book_id == book_id)
    if not book_ratings:
        return 0.0

    def load_seed():
        with open('data/seed.json','r') as f:
            data = json.load(f)

    total = reduce(lambda acc, r: acc + r.value, book_ratings, 0)
    return total / len(book_ratings)
def load_seed():
    """Load seed data from JSON file"""
    try:
        with open('data/seed.json','r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return{}