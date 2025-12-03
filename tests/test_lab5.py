# test_lazy.py
import unittest
from core.lazy import *
from core.domain import Book


class TestLazyComputations(unittest.TestCase):

    def setUp(self):
        # Create test books
        self.test_books = [
            Book("1", "Book One", "Author A", "Fiction", 2020, 4.5),
            Book("2", "Book Two", "Author B", "Non-Fiction", 2021, 4.2),
            Book("3", "Book Three", "Author C", "Fiction", 2019, 4.8),
            Book("4", "Book Four", "Author A", "Science", 2022, 4.1),
            Book("5", "Book Five", "Author D", "Fiction", 2020, 4.6),
        ]

        # Create simple taxonomy
        self.genre_tag = Tag("1", "Fiction")
        self.tags_tree = Tag("root", "All Tags", children=[self.genre_tag])

    def test_lazy_top_k_basic(self):
        stream = [("item1", 1.0), ("item2", 3.0), ("item3", 2.0)]
        results = list(lazy_top_k(stream, 2))

        self.assertEqual(len(results), 3)  # One result per stream element
        self.assertEqual(len(results[-1]), 2)  # Final top-2

    def test_lazy_top_k_empty(self):
        stream = []
        results = list(lazy_top_k(stream, 3))
        self.assertEqual(len(results), 0)

    def test_lazy_book_search(self):
        results = list(lazy_book_search(self.test_books, ["one", "two"], 4.0))
        self.assertEqual(len(results), 2)

    def test_lazy_book_search_no_results(self):
        results = list(lazy_book_search(self.test_books, ["nonexistent"], 4.0))
        self.assertEqual(len(results), 0)

    def test_batch_processing(self):
        batches = list(batch_process_books(self.test_books, 2))
        self.assertEqual(len(batches), 3)  # 5 books in batches of 2

    def test_taxonomy_iterator(self):
        def simple_predicate(book, genre_tag, book_tag):
            return book.genre == "Fiction"

        results = list(iter_books_by_taxonomy(
            self.test_books,
            self.genre_tag,
            self.tags_tree,
            simple_predicate
        ))

        self.assertEqual(len(results), 3)  # 3 fiction books


if __name__ == "__main__":
    unittest.main()


# ==================== Lab 8扩展测试：惰性计算性能 ====================

def test_lazy_computation_memory_efficiency():
    """测试惰性计算的内存效率"""
    import sys
    from core.lazy import lazy_top_k, lazy_book_search

    # 创建大型数据流
    large_stream = [(f"book_{i}", i * 0.1) for i in range(1000)]

    # 测试惰性top-K的内存使用
    initial_memory = sys.getsizeof(large_stream)

    top_k_generator = lazy_top_k(large_stream, 10)
    results = list(top_k_generator)

    final_memory = sys.getsizeof(results)

    # 验证惰性处理减少了内存使用
    assert final_memory < initial_memory * 0.5  # 内存使用减少至少50%


def test_lazy_search_performance():
    """测试惰性搜索性能"""
    from core.domain import Book
    import time

    # 创建测试书籍
    test_books = [
        Book(f"{i}", f"Book {i}", f"Author {i}", "Fiction", 2000 + i, 4.0)
        for i in range(100)
    ]

    # 测试惰性搜索时间
    start_time = time.time()
    results = list(lazy_book_search(test_books, ["Book"], 3.5))
    lazy_time = time.time() - start_time

    # 验证在合理时间内完成
    assert lazy_time < 1.0  # 1秒内完成
    assert len(results) > 0