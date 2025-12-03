import pytest
import asyncio
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.async_utils import AsyncRecoEngine, benchmark_recommendations
from core.services import AsyncRecoService, Recommendation
from core.domain import Book, User, Rating


@pytest.fixture
def sample_data():
    books = [
        Book("1", "Abai joly", "Mukhtar Auezov", "Classic", 1942, 4.8),
        Book("2", "Kan men ter", "Abdizhamil Nurpeisov", "Classic", 1970, 4.7),
        Book("3", "Akboz uy", "Ilyas Esenberlin", "History", 1973, 4.7),
    ]

    users = [
        User("u1", "Aliya"),
        User("u2", "Bauyrzhan"),
        User("u3", "Gani"),
    ]

    ratings = [
        Rating("u1", "1", 5), Rating("u1", "2", 4),
        Rating("u2", "3", 5), Rating("u2", "1", 3),
        Rating("u3", "2", 5), Rating("u3", "3", 4),
    ]

    return books, users, ratings


@pytest.fixture
def user_ids():
    return ["u1", "u2", "u3"]


@pytest.mark.asyncio
async def test_async_reco_engine_initialization():
    engine = AsyncRecoEngine(max_workers=3)
    assert engine.max_workers == 3
    engine.shutdown()


@pytest.mark.asyncio
async def test_parallel_recommendations(sample_data, user_ids):
    books, users, ratings = sample_data
    engine = AsyncRecoEngine(max_workers=2)

    recommendations = await engine.recommend_batch(user_ids, tuple(ratings), tuple(books), k=2)

    assert isinstance(recommendations, dict)
    assert len(recommendations) == len(user_ids)

    for user_id in user_ids:
        assert user_id in recommendations
        assert isinstance(recommendations[user_id], list)

    engine.shutdown()


@pytest.mark.asyncio
async def test_performance_metrics(sample_data):
    engine = AsyncRecoEngine(max_workers=2)

    metrics = await engine.get_performance_metrics()

    expected_keys = [
        "cache_hits", "cache_misses", "cache_size",
        "cache_max_size", "hit_ratio", "thread_pool_workers"
    ]

    for key in expected_keys:
        assert key in metrics

    assert metrics["thread_pool_workers"] == 2
    assert 0 <= metrics["hit_ratio"] <= 1

    engine.shutdown()


@pytest.mark.asyncio
async def test_async_reco_service(sample_data, user_ids):
    books, users, ratings = sample_data
    service = AsyncRecoService()

    report = await service.generate_parallel_report(user_ids, tuple(ratings), tuple(books), k=2)

    assert "timestamp" in report
    assert "total_processing_time_ms" in report
    assert "users_processed" in report
    assert "recommendations" in report

    assert report["users_processed"] == len(user_ids)
    assert len(report["recommendations"]) == len(user_ids)

    service.async_engine.shutdown()


@pytest.mark.asyncio
async def test_benchmark_function(sample_data, user_ids):
    books, users, ratings = sample_data

    benchmark_results = await benchmark_recommendations(
        user_ids[:3],  # 使用3个用户进行基准测试
        tuple(ratings),
        tuple(books),
        k=2
    )

    expected_keys = [
        "parallel_time_ms", "serial_time_ms", "speedup",
        "users_processed", "recommendations_per_user", "efficiency"
    ]

    for key in expected_keys:
        assert key in benchmark_results

    assert benchmark_results["users_processed"] == 3
    assert benchmark_results["recommendations_per_user"] == 2
    assert benchmark_results["parallel_time_ms"] >= 0
    assert benchmark_results["serial_time_ms"] >= 0


def test_user_statistics_calculation(sample_data):
    books, users, ratings = sample_data

    service = AsyncRecoService()

    user_stats = service._calculate_user_stats(
        ["u1", "u2", "u3"],
        tuple(ratings),
        tuple(books)
    )

    assert user_stats["total_users"] == 3
    assert "user_activity_levels" in user_stats
    assert "preferred_genres" in user_stats
    assert "average_ratings_per_user" in user_stats

    activity_levels = user_stats["user_activity_levels"]
    assert sum(activity_levels.values()) == 3


def test_recommendation_quality_analysis(sample_data):
    """测试推荐质量分析"""
    books, users, ratings = sample_data

    service = AsyncRecoService()

    # 创建模拟推荐数据 - 直接创建Recommendation对象
    mock_recommendations = {
        "u1": [
            Recommendation(
                book_id="1",
                title="Book 1",
                author="Author 1",
                genre="Classic",
                score=0.9,
                reason="Test reason"
            ),
            Recommendation(
                book_id="2",
                title="Book 2",
                author="Author 2",
                genre="History",
                score=0.8,
                reason="Test reason"
            )
        ],
        "u2": [
            Recommendation(
                book_id="3",
                title="Book 3",
                author="Author 3",
                genre="Poetry",
                score=0.7,
                reason="Test reason"
            )
        ],
        "u3": []  # 无推荐的用户
    }

    quality_metrics = service._analyze_recommendation_quality(
        mock_recommendations,
        tuple(books)
    )

    assert "average_score" in quality_metrics
    assert "success_rate" in quality_metrics
    assert "genre_diversity" in quality_metrics
    assert "top_recommended_books" in quality_metrics

    # 验证计算正确性
    assert 0.7 <= quality_metrics["average_score"] <= 0.9
    assert quality_metrics["success_rate"] == 2 / 3  # 2/3的用户有推荐
    assert quality_metrics["genre_diversity"] >= 2  # 至少2种类型


@pytest.mark.asyncio
async def test_empty_user_list(sample_data):
    """测试空用户列表处理"""
    books, users, ratings = sample_data

    engine = AsyncRecoEngine()

    recommendations = await engine.recommend_batch([], tuple(ratings), tuple(books))

    assert isinstance(recommendations, dict)
    assert len(recommendations) == 0

    engine.shutdown()


@pytest.mark.asyncio
async def test_large_number_of_users(sample_data):
    """测试大量用户处理"""
    books, users, ratings = sample_data

    # 创建15个测试用户（Lab 8要求）
    many_user_ids = [f"test_user_{i}" for i in range(15)]

    engine = AsyncRecoEngine(max_workers=5)

    start_time = time.time()
    recommendations = await engine.recommend_batch(
        many_user_ids, tuple(ratings), tuple(books), k=3
    )
    processing_time = (time.time() - start_time) * 1000

    # 验证性能：15个用户应该在合理时间内完成
    assert processing_time < 10000  # 10秒内完成
    assert len(recommendations) == 15

    # 验证大多数用户都有推荐
    users_with_recommendations = sum(1 for recs in recommendations.values() if recs)
    assert users_with_recommendations >= 10  # 至少10个用户有推荐

    engine.shutdown()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])