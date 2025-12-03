import asyncio
import concurrent.futures
import os
import time
import logging
from typing import List, Dict, Tuple, Any, Optional
from functools import partial

# Configure logging 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .memo import recommend_for_user_cached, get_cache_info
    from .domain import Book, Rating
    from .services import Recommendation
except ImportError:
    try:
        # If relative import fails, try absolute import
        from core.memo import recommend_for_user_cached, get_cache_info
        from core.domain import Book, Rating
        from core.services import Recommendation
    except ImportError as e:
        logger.error(f"Import failed: {e}")


        # Create fallback classes 创建备用类
        class Recommendation:
            def __init__(self, book_id, title, author, genre, score, reason):
                self.book_id = book_id
                self.title = title
                self.author = author
                self.genre = genre
                self.score = score
                self.reason = reason


class AsyncRecoEngine:
    """
    Asynchronous Recommendation Engine - Calculate recommendations for multiple users in parallel
    Uses ThreadPoolExecutor for CPU-intensive tasks
    """

    def __init__(self, max_workers: int = None):
        """
        Initialize recommendation engine

        Args:
            max_workers: Maximum worker threads for thread pool, defaults to CPU core count
        """
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="RecoWorker"
        )
        self._shutdown = False
        logger.info(f"Initialized async recommendation engine, worker threads: {self.max_workers}")

    async def recommend_batch(
            self,
            user_ids: List[str],
            ratings: Tuple[Rating, ...],
            books: Tuple[Book, ...],
            k: int = 5,
            timeout: Optional[float] = None
    ) -> Dict[str, List[Recommendation]]:
        """
        Calculate recommendations for multiple users in parallel

        Args:
            user_ids: List of user IDs
            ratings: Rating data
            books: Book data
            k: Number of recommendations per user
            timeout: Timeout in seconds

        Returns:
            Mapping of user IDs to recommendation lists
        """
        if self._shutdown:
            raise RuntimeError("Recommendation engine is shutdown")

        if not user_ids:
            logger.warning("No users to process")
            return {}

        logger.info(f"Starting parallel recommendation calculation for {len(user_ids)} users")
        start_time = time.perf_counter()

        # Create partial function to pass additional parameters异常处理：单个用户失败不影响其他用户
        recommend_func = partial(
            self._recommend_single_user,
            ratings=ratings,
            books=books,
            k=k
        )

        # Use ThreadPoolExecutor for parallel execution of CPU-intensive tasks
        loop = asyncio.get_event_loop()

        try:
            # Create tasks for each user
            tasks = [
                loop.run_in_executor(self.executor, recommend_func, user_id)
                for user_id in user_ids
            ]

            # Wait for all tasks to complete, with timeout support
            if timeout:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=timeout
                )
            else:
                results = await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.TimeoutError:
            logger.error(f"Recommendation calculation timeout, timeout: {timeout} seconds")
            raise
        except Exception as e:
            logger.error(f"Error during recommendation calculation: {e}")
            raise

        # Process results
        user_recommendations = {}
        successful_users = 0
        failed_users = 0

        for user_id, result in zip(user_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Recommendation calculation failed for user {user_id}: {result}")
                user_recommendations[user_id] = []
                failed_users += 1
            else:
                user_recommendations[user_id] = result
                successful_users += 1

        total_time = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Recommendation calculation completed: Successful {successful_users}/{len(user_ids)}, "
            f"Failed {failed_users}, Total time {total_time:.2f}ms"
        )

        if successful_users > 0:
            logger.info(f"Average time per user: {total_time / len(user_ids):.2f}ms")

        return user_recommendations

    def _recommend_single_user(
            self,
            user_id: str,
            ratings: Tuple[Rating, ...],
            books: Tuple[Book, ...],
            k: int = 5
    ) -> List[Recommendation]:
        """
        Calculate recommendations for a single user (executed in thread pool)

        Args:
            user_id: User ID
            ratings: Rating data
            books: Book data
            k: Number of recommendations

        Returns:
            List of recommendations
        """
        try:
            logger.debug(f"Starting recommendation calculation for user {user_id}")

            # Use cached recommendation function
            raw_recommendations = recommend_for_user_cached(user_id, ratings, books)

            # Convert to Recommendation objects
            recommendations = []
            for book_id, title, author, genre, score in raw_recommendations[:k]:
                recommendation = Recommendation(
                    book_id=book_id,
                    title=title,
                    author=author,
                    genre=genre,
                    score=score,
                    reason=self._generate_reason(score)
                )
                recommendations.append(recommendation)

            logger.debug(
                f"Recommendation calculation completed for user {user_id}, generated {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Recommendation calculation error for user {user_id}: {e}")
            return []

    def _generate_reason(self, score: float) -> str:
        """
        Generate recommendation reason based on score

        Args:
            score: Recommendation score

        Returns:
            Recommendation reason
        """
        if score > 0.8:
            return "Highly matches your reading preferences"
        elif score > 0.6:
            return "Matches your favorite book types"
        elif score > 0.4:
            return "Similar to books you like"
        else:
            return "Similar readers also like"

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics

        Returns:
            Performance metrics dictionary
        """
        cache_info = get_cache_info()
        total_requests = cache_info.hits + cache_info.misses
        hit_ratio = cache_info.hits / total_requests if total_requests > 0 else 0

        return {
            "cache_hits": cache_info.hits,
            "cache_misses": cache_info.misses,
            "cache_size": cache_info.currsize,
            "cache_max_size": cache_info.maxsize,
            "hit_ratio": hit_ratio,
            "thread_pool_workers": self.max_workers,
            "total_requests": total_requests,
            "engine_status": "shutdown" if self._shutdown else "running"
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Health check

        Returns:
            Health status information
        """
        metrics = await self.get_performance_metrics()
        return {
            "status": "healthy" if not self._shutdown else "shutdown",
            "workers": self.max_workers,
            "cache_effectiveness": metrics["hit_ratio"],
            "timestamp": time.time()
        }

    def shutdown(self):
        """Shutdown thread pool"""
        if not self._shutdown:
            logger.info("Shutting down recommendation engine...")
            self.executor.shutdown(wait=True)
            self._shutdown = True
            logger.info("Recommendation engine shutdown complete")


class AsyncRecoService:
    """
    High-level asynchronous recommendation service
    Provides a simplified interface for parallel recommendation generation
    """

    def __init__(self, max_workers: int = None):
        """
        Initialize recommendation service

        Args:
            max_workers: Maximum worker threads
        """
        self.engine = AsyncRecoEngine(max_workers)
        self.performance_history = []
    #生成完整并行报告
    async def generate_parallel_report(
            self,
            user_ids: List[str],
            ratings: Tuple[Rating, ...],
            books: Tuple[Book, ...],
            k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate comprehensive parallel recommendation report

        Args:
            user_ids: List of user IDs
            ratings: Rating data
            books: Book data
            k: Number of recommendations per user

        Returns:
            Comprehensive report with recommendations and metrics
        """
        start_time = time.time()

        # Generate recommendations
        recommendations = await self.engine.recommend_batch(user_ids, ratings, books, k)

        # Get performance metrics
        metrics = await self.engine.get_performance_metrics()

        # Calculate additional statistics
        total_recommendations = sum(len(recs) for recs in recommendations.values())
        user_statistics = self._calculate_user_statistics(user_ids, ratings)

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(recommendations, books)

        # Prepare report
        report = {
            "timestamp": time.time(),
            "total_processing_time_ms": (time.time() - start_time) * 1000,
            "users_processed": len(user_ids),
            "recommendations_per_user": k,
            "total_recommendations": total_recommendations,
            "recommendations": recommendations,
            "performance_metrics": metrics,
            "user_statistics": user_statistics,
            "quality_metrics": quality_metrics,
            "system_metrics": {
                "average_recommendation_score": quality_metrics["average_score"],
                "success_rate": quality_metrics["success_rate"],
                "genre_diversity": quality_metrics["genre_diversity"]
            }
        }

        # Store in performance history
        self.performance_history.append(report)

        return report
    #计算用户统计信息
    def _calculate_user_statistics(self, user_ids: List[str], ratings: Tuple[Rating, ...]) -> Dict[str, Any]:
        """Calculate user activity statistics"""
        user_ratings_count = {}
        for rating in ratings:
            if rating.user_id in user_ids:
                user_ratings_count[rating.user_id] = user_ratings_count.get(rating.user_id, 0) + 1

        # Categorize users by activity level
        activity_levels = {"high": 0, "medium": 0, "low": 0}
        for count in user_ratings_count.values():
            if count >= 10:
                activity_levels["high"] += 1
            elif count >= 5:
                activity_levels["medium"] += 1
            else:
                activity_levels["low"] += 1

        return {
            "user_activity_levels": activity_levels,
            "average_ratings_per_user": sum(user_ratings_count.values()) / len(user_ids) if user_ids else 0,
            "preferred_genres": self._get_preferred_genres(user_ids, ratings)
        }

    def _get_preferred_genres(self, user_ids: List[str], ratings: Tuple[Rating, ...]) -> Dict[str, int]:
        """Get preferred genres for the user group"""
        # Simplified implementation - in real system, you'd need book genre mapping
        genre_counts = {}
        for rating in ratings:
            if rating.user_id in user_ids and rating.value >= 4:
                # This is a simplified approach - you'd need actual book genre data
                genre_counts["General"] = genre_counts.get("General", 0) + 1
        return genre_counts
     #计算推荐质量指标
    def _calculate_quality_metrics(self, recommendations: Dict[str, List[Recommendation]], books: Tuple[Book, ...]) -> \
    Dict[str, Any]:
        """Calculate recommendation quality metrics """
        if not recommendations:
            return {
                "average_score": 0,
                "success_rate": 0,
                "genre_diversity": 0,
                "top_recommended_books": []
            }

        # Calculate average score
        all_scores = [rec.score for recs in recommendations.values() for rec in recs]
        average_score = sum(all_scores) / len(all_scores) if all_scores else 0

        # Calculate success rate (percentage of users who got recommendations)
        successful_users = sum(1 for recs in recommendations.values() if len(recs) > 0)
        success_rate = successful_users / len(recommendations) if recommendations else 0

        # Calculate genre diversity
        genres = set()
        for recs in recommendations.values():
            for rec in recs:
                genres.add(rec.genre)
        genre_diversity = len(genres)

        # Find top recommended books
        book_recommendation_count = {}
        for recs in recommendations.values():
            for rec in recs:
                book_recommendation_count[rec.book_id] = book_recommendation_count.get(rec.book_id, 0) + 1

        top_books = []
        for book_id, count in sorted(book_recommendation_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            book = next((b for b in books if b.id == book_id), None)
            if book:
                top_books.append({
                    "title": book.title,
                    "author": book.author,
                    "genre": book.genre,
                    "recommendation_count": count
                })

        return {
            "average_score": round(average_score, 3),
            "success_rate": round(success_rate, 3),
            "genre_diversity": genre_diversity,
            "top_recommended_books": top_books
        }

    def get_performance_history(self) -> List[Dict[str, Any]]:
        """Get performance history"""
        return self.performance_history.copy()

    def clear_history(self):
        """Clear performance history"""
        self.performance_history.clear()

    async def shutdown(self):
        """Shutdown the service"""
        self.engine.shutdown()


#  benchmark_recommendations 函数
async def benchmark_recommendations(
        user_ids: List[str],
        ratings: Tuple[Rating, ...],
        books: Tuple[Book, ...],
        k: int = 5,
        max_workers: int = None
) -> Dict[str, Any]:
    """
    Benchmark: Compare performance of parallel and serial computation

    Args:
        user_ids: List of user IDs
        ratings: Rating data
        books: Book data
        k: Number of recommendations
        max_workers: Maximum worker threads

    Returns:
        Performance test results
    """
    if not user_ids:
        logger.warning("Benchmark: No users to process")
        return {
            "parallel_time_ms": 0,
            "serial_time_ms": 0,
            "speedup": 0,
            "users_processed": 0,
            "recommendations_per_user": k,
            "efficiency": 0,
            "status": "skipped"
        }

    logger.info(f"Starting performance benchmark, number of users: {len(user_ids)}")

    # 创建异步引擎
    async_engine = AsyncRecoEngine(max_workers=max_workers)

    try:
        # 并行计算
        parallel_start = time.perf_counter()
        parallel_results = await async_engine.recommend_batch(user_ids, ratings, books, k)
        parallel_time = (time.perf_counter() - parallel_start) * 1000

        # 串行计算（用于对比）
        serial_start = time.perf_counter()
        serial_results = {}

        # 使用相同的函数进行串行计算
        for user_id in user_ids:
            try:
                raw_recs = recommend_for_user_cached(user_id, ratings, books)
                serial_results[user_id] = [
                    Recommendation(
                        book_id=book_id,
                        title=title,
                        author=author,
                        genre=genre,
                        score=score,
                        reason="Benchmark test"
                    )
                    for book_id, title, author, genre, score in raw_recs[:k]
                ]
            except Exception as e:
                logger.error(f"Serial recommendation failed for user {user_id}: {e}")
                serial_results[user_id] = []

        serial_time = (time.perf_counter() - serial_start) * 1000

        # 计算性能指标
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        efficiency = speedup / (max_workers or min(32, (os.cpu_count() or 1) + 4))

        # 验证结果一致性
        results_match = all(
            len(parallel_results.get(user_id, [])) == len(serial_results.get(user_id, []))
            for user_id in user_ids
        )

        # 获取性能指标
        metrics = await async_engine.get_performance_metrics()

        result = {
            "parallel_time_ms": round(parallel_time, 2),
            "serial_time_ms": round(serial_time, 2),
            "speedup": round(speedup, 2),
            "users_processed": len(user_ids),
            "recommendations_per_user": k,
            "efficiency": round(efficiency, 2),
            "max_workers": max_workers,
            "results_consistent": results_match,
            "cache_hit_ratio": round(metrics["hit_ratio"], 3),
            "status": "completed"
        }

        logger.info(f"Benchmark completed: Speedup {speedup:.2f}x, Efficiency {efficiency:.2f}")
        return result

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return {
            "parallel_time_ms": 0,
            "serial_time_ms": 0,
            "speedup": 0,
            "users_processed": len(user_ids),
            "recommendations_per_user": k,
            "efficiency": 0,
            "error": str(e),
            "status": "failed"
        }
    finally:
        # 确保关闭引擎
        async_engine.shutdown()


# 简化的演示函数，避免复杂的依赖
async def demo_simple():
    """简化的演示函数"""
    print("Async recommendation engine is ready!")

    # 创建模拟数据
    class MockBook:
        def __init__(self, id, title, author, genre, year, rating):
            self.id = id
            self.title = title
            self.author = author
            self.genre = genre
            self.year = year
            self.rating = rating

    class MockRating:
        def __init__(self, user_id, book_id, value):
            self.user_id = user_id
            self.book_id = book_id
            self.value = value

    # 创建测试数据
    books = [MockBook(f"book{i}", f"Book {i}", f"Author {i}", "Fiction", 2020, 4.5) for i in range(10)]
    ratings = [MockRating("user1", f"book{i}", 4) for i in range(5)]

    user_ids = ["user1", "user2", "user3"]

    # 测试引擎
    engine = AsyncRecoEngine(max_workers=2)

    try:
        # 由于没有真实的推荐函数，这里会返回空结果但不会报错
        results = await engine.recommend_batch(user_ids, tuple(ratings), tuple(books), k=3)
        print(f"Demo completed. Results for {len(results)} users.")

    except Exception as e:
        print(f"Demo completed with expected error (no real recommendation function): {e}")
    finally:
        engine.shutdown()


if __name__ == "__main__":
    # 运行简化演示
    asyncio.run(demo_simple())