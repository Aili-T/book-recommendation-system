import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.domain import Book, User, Rating
from core.transforms import *


class TestLab1:
    """测试Lab1的纯函数和不可变性"""

    def test_immutable_data_classes(self):
        """测试数据类的不可变性"""
        book = Book("1", "Test Book", "Test Author", "Fiction", 2020, 4.5)
        user = User("u1", "Test User")
        rating = Rating("u1", "1", 5)

        # 测试不可变性 - 应该不能修改属性（会抛出异常）
        try:
            book.title = "New Title"
            assert False, "Book should be immutable"
        except:
            assert True

        try:
            user.name = "New Name"
            assert False, "User should be immutable"
        except:
            assert True

        try:
            rating.value = 3
            assert False, "Rating should be immutable"
        except:
            assert True

    def test_filter_books_by_year(self):
        """测试按年份过滤书籍"""
        books = (
            Book("1", "Book 1", "Author 1", "Fiction", 2010, 4.0),
            Book("2", "Book 2", "Author 2", "Fiction", 2020, 4.5),
            Book("3", "Book 3", "Author 3", "Fiction", 2022, 4.2),
        )

        # 测试过滤2020年后的书籍
        result = filter_books_by_year(books, 2020)
        assert len(result) == 2
        assert all(book.year >= 2020 for book in result)

    def test_filter_books_by_genre(self):
        """测试按类型过滤书籍"""
        books = (
            Book("1", "Sci-Fi Book", "Author 1", "Sci-Fi", 2020, 4.5),
            Book("2", "Fantasy Book", "Author 2", "Fantasy", 2020, 4.3),
            Book("3", "Sci-Fi Book 2", "Author 3", "Sci-Fi", 2021, 4.7),
        )

        # 测试过滤Sci-Fi类型的书籍
        result = filter_books_by_genre(books, "Sci-Fi")
        assert len(result) == 2
        assert all(book.genre == "Sci-Fi" for book in result)

    def test_get_book_titles(self):
        """测试提取书籍标题"""
        books = (
            Book("1", "Python Guide", "Author 1", "Education", 2020, 4.5),
            Book("2", "ML Basics", "Author 2", "Education", 2021, 4.3),
        )

        # 测试映射函数
        titles = get_book_titles(books)
        assert titles == ("Python Guide", "ML Basics")
        assert isinstance(titles, tuple)  # 确保返回的是元组

    def test_get_average_rating(self):
        """测试计算平均评分"""
        books = (
            Book("1", "Book 1", "Author 1", "Fiction", 2020, 4.0),
            Book("2", "Book 2", "Author 2", "Fiction", 2021, 4.5),
            Book("3", "Book 3", "Author 3", "Fiction", 2022, 4.5),
        )

        # 测试归约函数
        avg_rating = get_average_rating(books)
        expected_avg = (4.0 + 4.5 + 4.5) / 3
        assert avg_rating == pytest.approx(expected_avg, 0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])