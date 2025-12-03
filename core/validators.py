from typing import Tuple, List
from .ftypes import Maybe, Just, Nothing, Either, Right, Left, maybe
from .domain import Book, Rating, Review, User


def safe_book(books: Tuple[Book, ...], book_id: str) -> Maybe[Book]:
    """安全地获取书籍，返回Maybe[Book]"""
    for book in books:
        if book.id == book_id:
            return Just(book)
    return Nothing()


def safe_user(users: Tuple[User, ...], user_id: str) -> Maybe[User]:
    """安全地获取用户，返回Maybe[User]"""
    for user in users:
        if user.id == user_id:
            return Just(user)
    return Nothing()


def validate_rating(rating: Rating,
                    books: Tuple[Book, ...],
                    users: Tuple[User, ...],
                    existing_ratings: Tuple[Rating, ...]) -> Either[str, Rating]:
    """验证评分：1-5分，用户和书籍存在，没有重复评分"""

    # 检查评分范围
    if not (1 <= rating.value <= 5):
        return Left(f"Rating must be between 1-5, currently：{rating.value}")

    # 检查用户是否存在
    user_exists = any(user.id == rating.user_id for user in users)
    if not user_exists:
        return Left(f"User does not exist：{rating.user_id}")

    # 检查书籍是否存在
    book_exists = any(book.id == rating.book_id for book in books)
    if not book_exists:
        return Left(f"Book does not exist：{rating.book_id}")

    # 检查重复评分
    duplicate = any(
        r.user_id == rating.user_id and r.book_id == rating.book_id
        for r in existing_ratings
    )
    if duplicate:
        return Left(f"User {rating.user_id} Already on books {rating.book_id} Rated")

    return Right(rating)


def validate_review(review: Review,
                    books: Tuple[Book, ...],
                    users: Tuple[User, ...],
                    existing_reviews: Tuple[Review, ...]) -> Either[str, Review]:
    """验证评论：用户和书籍存在，文本不为空"""

    # 检查用户是否存在
    user_exists = any(user.id == review.user_id for user in users)
    if not user_exists:
        return Left(f"User does not exist：{review.user_id}")

    # 检查书籍是否存在
    book_exists = any(book.id == review.book_id for book in books)
    if not book_exists:
        return Left(f"Book does not exist：{review.book_id}")

    # 检查评论文本
    if not review.text or not review.text.strip():
        return Left("Comment content cannot be empty")

    # 检查重复评论（可选）
    duplicate = any(
        r.user_id == review.user_id and r.book_id == review.book_id
        for r in existing_reviews
    )
    if duplicate:
        return Left(f"User {review.user_id} Already on books  {review.book_id} Rated")

    return Right(review)


def add_rating_pipeline(new_rating: Rating,
                        ratings: Tuple[Rating, ...],
                        books: Tuple[Book, ...],
                        users: Tuple[User, ...]) -> Either[str, Tuple[Rating, ...]]:
    """添加评分 + 重新计算平均评分的完整流程"""

    # 验证新评分
    validation_result = validate_rating(new_rating, books, users, ratings)

    # 使用bind连接操作：如果验证成功，则添加评分
    return validation_result.bind(
        lambda valid_rating: Right(ratings + (valid_rating,))
    )


def add_review_pipeline(new_review: Review,
                        reviews: Tuple[Review, ...],
                        books: Tuple[Book, ...],
                        users: Tuple[User, ...]) -> Either[str, Tuple[Review, ...]]:
    """添加评论的完整流程"""

    # 验证新评论
    validation_result = validate_review(new_review, books, users, reviews)

    # 使用bind连接操作：如果验证成功，则添加评论
    return validation_result.bind(
        lambda valid_review: Right(reviews + (valid_review,))
    )


def calculate_avg_rating_safe(ratings: Tuple[Rating, ...], book_id: str) -> Maybe[float]:
    """安全地计算平均评分，返回Maybe[float]"""
    book_ratings = [r.value for r in ratings if r.book_id == book_id]

    if not book_ratings:
        return Nothing()

    avg_rating = sum(book_ratings) / len(book_ratings)
    return Just(avg_rating)


# 组合操作示例
def get_book_rating_info(books: Tuple[Book, ...],
                         ratings: Tuple[Rating, ...],
                         book_id: str) -> str:
    """组合操作：获取书籍评分信息"""

    # 使用Maybe处理可能不存在的书籍
    book_maybe = safe_book(books, book_id)

    # 使用map和get_or_else安全地处理
    return book_maybe.map(
        lambda book: calculate_avg_rating_safe(ratings, book_id)
        .map(lambda avg: f"《{book.title}》Average rating: {avg:.2f}")
        .get_or_else(f"《{book.title}》No rating yet")
    ).get_or_else(f"books ID {book_id} does not exist")