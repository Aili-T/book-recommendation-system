import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.compose import compose, pipe
from core.services import LibraryService, RecoService, DayReport
from core.domain import Book, User, Rating


def test_compose_basic():
    """测试基础函数组合 Testing Basic Function Combinations"""

    def double(x): return x * 2

    def increment(x): return x + 1

    composed = compose(double, increment)
    result = composed(3)
    assert result == 8  # double(increment(3)) = double(4) = 8
    print("✅ test_compose_basic passed")


def test_pipe_basic():
    """测试管道操作Test Pipeline Operations"""

    def double(x): return x * 2

    def increment(x): return x + 1

    result = pipe(3, increment, double)
    assert result == 8  # double(increment(3)) = double(4) = 8
    print("✅ test_pipe_basic passed")


def test_library_service_initialization():
    """测试LibraryService初始化 Testing LibraryService Initialization"""
    validators = {'rating': lambda x, b, u, r: x}
    selectors = {'user_books': lambda u, r, b: []}
    calculators = {'average_rating': lambda r: 0.0}

    service = LibraryService(validators, selectors, calculators)
    assert service.validators == validators
    assert service.selectors == selectors
    assert service.calculators == calculators
    print("✅ test_library_service_initialization passed")


def test_reco_service_initialization():
    """测试RecoService初始化"""

    def mock_recommend(user_id, ratings, books):
        return [("1", 0.9)]

    postfilters = [lambda x: x]
    service = RecoService(mock_recommend, postfilters)

    assert service.recommend == mock_recommend
    assert service.postfilters == postfilters
    print("✅ test_reco_service_initialization passed")


def test_day_report_structure():
    """测试日报表结构Test Daily Report Structure"""
    books = [Book("1", "Test Book", "Author", "Fiction", 2020, 4.5)]
    users = [User("u1", "Test User")]
    ratings = [Rating("u1", "1", 5)]

    validators = {'rating': lambda x, b, u, r: x}
    selectors = {'user_books': lambda u, r, b: []}
    calculators = {'average_rating': lambda r: 4.5}

    service = LibraryService(validators, selectors, calculators)
    report = service.day_report("2024-01-15", books, users, ratings)

    assert isinstance(report, DayReport)
    assert report.total_books == 1
    assert report.total_users == 1
    print("✅ test_day_report_structure passed")


if __name__ == "__main__":
    test_compose_basic()
    test_pipe_basic()
    test_library_service_initialization()
    test_reco_service_initialization()
    test_day_report_structure()
    print("🎉All 5 tests passed! ")


# ==================== Lab 8扩展测试：服务管道性能 ====================

def test_service_pipeline_performance():
    """测试服务管道的性能"""
    from core.services import LibraryService, RecoService
    from core.domain import Book, User, Rating
    import time

    # 创建测试数据
    books = [Book("1", "Test Book", "Author", "Fiction", 2020, 4.5)]
    users = [User("u1", "Test User")]
    ratings = [Rating("u1", "1", 5)]

    # 测试LibraryService性能
    validators = {'rating': lambda x, b, u, r: x}
    selectors = {'user_books': lambda u, r, b: []}
    calculators = {'average_rating': lambda r: 4.5}

    library_service = LibraryService(validators, selectors, calculators)

    start_time = time.time()
    report = library_service.day_report("2024-01-15", books, users, ratings)
    library_time = (time.time() - start_time) * 1000

    # 验证在合理时间内完成
    assert library_time < 1000  # 1秒内完成
    assert report.total_books == 1


def test_reco_service_with_filters():
    """测试带过滤器的推荐服务"""
    from core.services import RecoService, simple_recommend

    def mock_recommend(user_id, ratings, books):
        return [("1", 0.9), ("2", 0.8), ("3", 0.7)]

    # 创建带过滤器的推荐服务
    postfilters = [
        lambda recs: [r for r in recs if r[1] > 0.75]  # 只保留分数>0.75的
    ]

    reco_service = RecoService(mock_recommend, postfilters)

    # 测试过滤功能
    recommendations = reco_service.recommend_top("u1", 5, [], [], [])

    # 验证过滤器工作正常
    assert len(recommendations) <= 2  # 只有2个推荐分数>0.75
    if recommendations:
        assert all(rec.score > 0.75 for rec in recommendations)