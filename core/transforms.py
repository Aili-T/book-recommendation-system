from functools import reduce
from typing import Tuple


# 纯函数示例
def filter_books_by_year(books: Tuple, min_year: int) -> Tuple:
    """过滤指定年份之后的书籍"""
    return tuple(filter(lambda b: b.year >= min_year, books))


def filter_books_by_genre(books: Tuple, genre: str) -> Tuple:
    """按类型过滤书籍"""
    return tuple(filter(lambda b: b.genre == genre, books))


def get_book_titles(books: Tuple) -> Tuple[str, ...]:
    """提取书名列表"""
    return tuple(map(lambda b: b.title, books))


def get_average_rating(books: Tuple) -> float:
    """计算所有书籍的平均评分"""
    if not books:
        return 0.0
    total = reduce(lambda acc, b: acc + b.rating, books, 0)
    return total / len(books)


# Lab1 要求的函数
def add_rating(ratings: Tuple, new_rating) -> Tuple:
    """添加新评分（返回新元组）"""
    return ratings + (new_rating,)


def avg_rating_for_book(ratings: Tuple, book_id: str) -> float:
    """计算某本书的平均评分"""
    book_ratings = tuple(r for r in ratings if r.book_id == book_id)
    if not book_ratings:
        return 0.0

    total = reduce(lambda acc, r: acc + r.value, book_ratings, 0)
    return total / len(book_ratings)