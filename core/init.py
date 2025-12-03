# Core module for functional programming patterns
from .compose import compose, pipe, identity, constant, tap
from .services import (
    LibraryService, RecoService, DayReport, Recommendation,
    simple_recommend, filter_already_read, filter_by_genre,
    filter_by_rating, boost_recent_books,
    calculate_average_rating, calculate_user_average_rating, calculate_favorite_genre,
    select_user_books, select_user_ratings,
    AsyncRecoService  # 添加这一行
)
from .async_utils import AsyncRecoEngine, benchmark_recommendations

__all__ = [
    'compose', 'pipe', 'identity', 'constant', 'tap',
    'LibraryService', 'RecoService', 'DayReport', 'Recommendation',
    'simple_recommend', 'filter_already_read', 'filter_by_genre',
    'filter_by_rating', 'boost_recent_books',
    'calculate_average_rating', 'calculate_user_average_rating', 'calculate_favorite_genre',
    'select_user_books', 'select_user_ratings',
    'AsyncRecoEngine', 'AsyncRecoService', 'benchmark_recommendations'
]