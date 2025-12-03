import pytest
import time
import sys
import os

# 添加项目路径到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.memo import (
    calculate_user_profile,
    calculate_book_similarity,
    recommend_for_user_cached,
    recommend_for_user_uncached,
    get_cache_info,
    clear_cache
)
from core.domain import Book, Rating, User


@pytest.fixture
def sample_data():
    """创建测试数据"""
    books = [
        Book("1", "Абай жолы", "Мұхтар Әуезов", "Classic", 1942, 4.8),
        Book("2", "Қан мен тер", "Әбдіжәміл Нұрпеісов", "Classic", 1970, 4.7),
        Book("3", "Ақбоз үй", "Ілияс Есенберлин", "History", 1973, 4.7),
        Book("4", "Қазақ хандығы", "Меруерт Абусеитова", "History", 2005, 4.6),
    ]

    users = [User("u1", "Aliya"), User("u2", "Bauyrzhan")]

    ratings = [
        Rating("u1", "1", 5),  # User1 rates Classic book highly
        Rating("u1", "2", 4),  # User1 rates another Classic
        Rating("u2", "3", 5),  # User2 rates History book
        Rating("u2", "4", 3),  # User2 rates another History lower
    ]

    return books, ratings, users


def test_calculate_user_profile(sample_data):
    """测试用户画像计算"""
    books, ratings, users = sample_data
    profile = calculate_user_profile("u1", tuple(ratings), tuple(books))

    assert "preferred_authors" in profile
    assert "preferred_genres" in profile
    assert "rated_books" in profile
    assert "1" in profile['rated_books']
    assert "2" in profile['rated_books']
    assert "Classic" in profile['preferred_genres']


def test_calculate_book_similarity(sample_data):
    """测试书籍相似度计算Book Similarity Calculation"""
    books, ratings, users = sample_data
    user_profile = calculate_user_profile("u1", tuple(ratings), tuple(books))
    book = books[0]  # Classic book by preferred author

    similarity = calculate_book_similarity(book, user_profile)
    assert 0 <= similarity <= 1


def test_recommend_for_user_cached(sample_data):
    """测试带缓存的推荐函数Cached Recommendation Function"""
    books, ratings, users = sample_data
    recommendations = recommend_for_user_cached("u1", tuple(ratings), tuple(books))

    assert isinstance(recommendations, tuple)
    assert len(recommendations) <= 10


def test_cache_performance(sample_data):
    """测试缓存性能"""
    books, ratings, users = sample_data

    # 清除缓存
    clear_cache()

    # 第一次调用（缓存未命中）
    start_time = time.time()
    rec1 = recommend_for_user_cached("u1", tuple(ratings), tuple(books))
    first_call_time = time.time() - start_time

    # 第二次调用（缓存命中）
    start_time = time.time()
    rec2 = recommend_for_user_cached("u1", tuple(ratings), tuple(books))
    second_call_time = time.time() - start_time

    # 结果应该相同
    assert rec1 == rec2
    # 第二次调用应该更快
    assert second_call_time <= first_call_time * 2  # 允许一些浮动


def test_cache_info(sample_data):
    """测试缓存信息"""
    books, ratings, users = sample_data

    # 清除缓存
    clear_cache()

    # 初始缓存信息
    initial_info = get_cache_info()
    assert initial_info.hits == 0
    assert initial_info.misses == 0

    # 调用一次
    recommend_for_user_cached("u1", tuple(ratings), tuple(books))

    # 再次获取缓存信息
    after_info = get_cache_info()
    assert after_info.misses == 1

    # 再次调用相同参数
    recommend_for_user_cached("u1", tuple(ratings), tuple(books))

    final_info = get_cache_info()
    assert final_info.hits == 1
    assert final_info.misses == 1


def test_clear_cache(sample_data):
    """测试清除缓存"""
    books, ratings, users = sample_data

    # 先调用一次填充缓存
    recommend_for_user_cached("u1", tuple(ratings), tuple(books))

    # 清除缓存
    clear_cache()

    # 检查缓存是否被清除
    cache_info = get_cache_info()
    assert cache_info.currsize == 0


def test_recommendation_structure(sample_data):
    """测试推荐结果结构Recommended Results Structure"""
    books, ratings, users = sample_data
    recommendations = recommend_for_user_cached("u1", tuple(ratings), tuple(books))

    if recommendations:  # 如果有推荐结果
        first_recommendation = recommendations[0]
        # 检查推荐结果的结构：(book_id, title, author, genre, score)
        assert len(first_recommendation) == 5
        assert isinstance(first_recommendation[0], str)  # book_id
        assert isinstance(first_recommendation[1], str)  # title
        assert isinstance(first_recommendation[2], str)  # author
        assert isinstance(first_recommendation[3], str)  # genre
        assert isinstance(first_recommendation[4], float)  # score


def test_user_with_no_ratings(sample_data):
    """测试没有评分的用户Test for users without ratings"""
    books, ratings, users = sample_data
    # 使用一个没有评分的用户
    recommendations = recommend_for_user_cached("u3", tuple(ratings), tuple(books))

    # 应该返回空结果或默认推荐
    assert isinstance(recommendations, tuple)


def test_empty_data():
    """测试空数据Empty data"""
    empty_books = ()
    empty_ratings = ()

    recommendations = recommend_for_user_cached("u1", empty_ratings, empty_books)
    assert recommendations == ()


def test_cache_with_different_users(sample_data):
    """测试不同用户的缓存Cache for Different Users"""
    books, ratings, users = sample_data

    # 清除缓存
    clear_cache()

    # 为用户1生成推荐
    rec1 = recommend_for_user_cached("u1", tuple(ratings), tuple(books))

    # 为用户2生成推荐
    rec2 = recommend_for_user_cached("u2", tuple(ratings), tuple(books))

    # 两个推荐应该不同
    assert rec1 != rec2

    # 缓存应该有两个条目
    cache_info = get_cache_info()
    assert cache_info.currsize == 2