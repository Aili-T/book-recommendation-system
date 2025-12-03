import pytest
import sys
import os

# 添加项目路径到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.ftypes import Maybe, Just, Nothing, Either, Right, Left
from core.validators import (
    safe_book, validate_rating, validate_review,
    add_rating_pipeline, calculate_avg_rating_safe,
    get_book_rating_info
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

    users = [
        User("u1", "Aliya"),
        User("u2", "Bauyrzhan"),
        User("u3", "Gani"),
    ]

    ratings = [
        Rating("u1", "1", 5),
        Rating("u2", "1", 4),
        Rating("u1", "2", 3),
    ]

    return books, users, ratings


# ==================== Maybe 类型测试 ====================

def test_maybe_just_creation():
    """测试Just创建和基本属性"""
    just_value = Just(42)

    assert just_value.is_just() == True
    assert just_value.is_nothing() == False
    assert just_value.get_or_else(0) == 42


def test_maybe_nothing_creation():
    """测试Nothing创建和基本属性"""
    nothing = Nothing()

    assert nothing.is_just() == False
    assert nothing.is_nothing() == True
    assert nothing.get_or_else(42) == 42


def test_maybe_map_just():
    """测试Just的map操作"""
    just_value = Just(10)
    mapped = just_value.map(lambda x: x * 2)

    assert mapped.is_just() == True
    assert mapped.get_or_else(0) == 20


def test_maybe_map_nothing():
    """测试Nothing的map操作"""
    nothing = Nothing()
    mapped = nothing.map(lambda x: x * 2)

    assert mapped.is_nothing() == True
    assert mapped.get_or_else(100) == 100


# 继续其他测试方法...