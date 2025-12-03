from functools import lru_cache
from typing import Tuple
import time
from core.domain import Book, Rating, User
from core.transforms import avg_rating_for_book

#Recommendation Function
def calculate_user_profile(user_id: str, ratings: Tuple[Rating, ...], books: Tuple[Book, ...]) -> dict:
    """Calculate user profile：基于用户评分过的书籍的特征"""
    user_ratings = [r for r in ratings if r.user_id == user_id]

    # Collect user preferences
    preferred_authors = set()
    preferred_genres = set()

    for rating in user_ratings:
        if rating.value >= 4:  # 只考虑高评分
            book = next((b for b in books if b.id == rating.book_id), None)
            if book:
                preferred_authors.add(book.author)
                preferred_genres.add(book.genre)

    return {
        'preferred_authors': tuple(preferred_authors),
        'preferred_genres': tuple(preferred_genres),
        'rated_books': tuple(r.book_id for r in user_ratings)
    }


def calculate_book_similarity(book: Book, user_profile: dict) -> float:
    """计算书籍与用户画像的相似度"""
    score = 0.0

    # 作者匹配
    if book.author in user_profile['preferred_authors']:
        score += 2.0

    # 体裁匹配
    if book.genre in user_profile['preferred_genres']:
        score += 1.5

    # 归一化
    max_possible = 3.5  # 作者2.0 + 体裁1.5

    return score / max_possible if max_possible > 0 else 0

#Memoization Implementation
@lru_cache(maxsize=128)
def recommend_for_user_cached(
        user_id: str,
        ratings_index: Tuple[Rating, ...],
        books_index: Tuple[Book, ...]
) -> Tuple[Tuple[str, str, str, str, float], ...]:
    """Content-based recommendation algorithm (with cache"""
    start_time = time.time()
    #Content-based algorithm
    user_profile = calculate_user_profile(user_id, ratings_index, books_index)

    # Exclude rated books
    unrated_books = [b for b in books_index if b.id not in user_profile['rated_books']]

    # 计算每本书的推荐分数
    book_scores = []
    for book in unrated_books:
        similarity = calculate_book_similarity(book, user_profile)

        # 结合书籍的平均评分
        avg_rating = avg_rating_for_book(ratings_index, book.id)
        final_score = similarity * 0.7 + (avg_rating / 5.0) * 0.3

        book_scores.append((book.id, book.title, book.author, book.genre, final_score))

    # 按分数排序，返回前10本
    book_scores.sort(key=lambda x: x[4], reverse=True)  # 按分数排序
    top_books = book_scores[:10]

    end_time = time.time()
    print(f"Recommendation computation time: {(end_time - start_time) * 1000:.2f}ms")

    return tuple(top_books)


def recommend_for_user_uncached(
        user_id: str,
        ratings_index: Tuple[Rating, ...],
        books_index: Tuple[Book, ...]
) -> Tuple[Tuple[str, str, str, str, float], ...]:
    """无缓存版本的推荐算法（用于性能对比）"""
    # 清除缓存以确保公平比较
    recommend_for_user_cached.cache_clear()
    return recommend_for_user_cached(user_id, ratings_index, books_index)


def get_cache_info():
    """获取缓存信息"""
    return recommend_for_user_cached.cache_info()


def clear_cache():
    """清除缓存"""
    recommend_for_user_cached.cache_clear()