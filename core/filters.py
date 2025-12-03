# core/filters.py
from typing import Callable, Tuple, List
from core.domain import Book


  #closure and Lambda

def create_genre_filter(genre: str) -> Callable[[Book], bool]:
    """Create a closure for the type filter"""

    def genre_filter(book: Book) -> bool:
        return book.genre.lower() == genre.lower()

    return genre_filter


def create_rating_filter(min_rating: float = 0.0, max_rating: float = 5.0) -> Callable[[Book], bool]:
    """Create a closure for the rating range filter"""

    def rating_filter(book: Book) -> bool:
        return min_rating <= book.rating <= max_rating

    return rating_filter


def create_year_range_filter(start_year: int = 1900, end_year: int = 2025) -> Callable[[Book], bool]:
    """Create a closure for the year range filter"""

    def year_filter(book: Book) -> bool:
        return start_year <= book.year <= end_year

    return year_filter


def create_author_filter(author_name: str) -> Callable[[Book], bool]:
    """Create a closure for the author filter"""

    def author_filter(book: Book) -> bool:
        return author_name.lower() in book.author.lower()

    return author_filter


#Higher-order functions for combining filters
def combine_filters(*filters: Callable[[Book], bool]) -> Callable[[Book], bool]:
    """Closures that combine multiple filters"""

    def combined_filter(book: Book) -> bool:
        return all(filter_func(book) for filter_func in filters)

    return combined_filter


# Configurable Closure
def create_advanced_search(
        genres: List[str] = None,
        min_rating: float = 0,
        max_rating: float = 5.0,
        start_year: int = 1900,
        end_year: int = 2025,
        authors: List[str] = None
) -> Callable[[Tuple[Book, ...]], Tuple[Book, ...]]:
    """Creating a closure for an advanced search function"""

    filters = []

    # 使用lambda处理多个类型
    if genres:
        genre_lambda = lambda book: any(genre.lower() == book.genre.lower() for genre in genres)
        filters.append(genre_lambda)

    # 评分过滤
    if min_rating > 0 or max_rating < 5.0:
        filters.append(create_rating_filter(min_rating, max_rating))

    # 年份过滤
    if start_year > 1900 or end_year < 2025:
        filters.append(create_year_range_filter(start_year, end_year))

    # 作者过滤
    if authors:
        author_lambda = lambda book: any(author.lower() in book.author.lower() for author in authors)
        filters.append(author_lambda)

    def search_function(books: Tuple[Book, ...]) -> Tuple[Book, ...]:
        if not filters:
            return books

        combined = combine_filters(*filters)
        return tuple(filter(combined, books))

    return search_function



def create_recommendation_configurator(preferred_genres: List[str], min_rating: float = 4.0):

    def recommend_books(books: Tuple[Book, ...]) -> Tuple[Book, ...]:
        genre_filter = lambda book: any(genre.lower() == book.genre.lower() for genre in preferred_genres)
        rating_filter = create_rating_filter(min_rating)

        combined = combine_filters(genre_filter, rating_filter)
        return tuple(filter(combined, books))

    return recommend_books