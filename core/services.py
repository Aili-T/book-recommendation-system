import time
from typing import Callable, List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from .compose import pipe, compose
from .domain import Book, Rating
from .async_utils import AsyncRecoEngine, benchmark_recommendations


@dataclass
class DayReport:
    """Report for a single day"""
    date: str
    total_books: int
    total_users: int
    total_ratings: int
    average_rating: float
    popular_genres: List[Tuple[str, int]]
    active_users: List[Tuple[str, int]]


@dataclass
class Recommendation:
    """Book recommendation with metadata"""
    book_id: str
    title: str
    author: str
    genre: str
    score: float
    reason: str


class LibraryService:

    #Facade service for library operations without business logic.
    # All logic is injected as pure functions.


    def __init__(self,
                 validators: Dict[str, Callable],
                 selectors: Dict[str, Callable],
                 calculators: Dict[str, Callable]):
        self.validators = validators
        self.selectors = selectors
        self.calculators = calculators

    def day_report(self, day: str, books, users, ratings) -> DayReport:
        """Generate daily report using composed functions"""
        # Compose the report generation pipeline
        report_data = self._select_day_data(day)((books, users, ratings))
        stats = self._calculate_basic_stats(report_data)
        return self._enrich_with_metrics(stats)

    def _select_day_data(self, day: str) -> Callable:
        """Select data for specific day (simplified)"""

        def selector(data):
            books, users, ratings = data
            # In a real system, we would filter by date
            # For demo, we'll use all data
            return (books, users, ratings)

        return selector

    def _calculate_basic_stats(self, data) -> Dict[str, Any]:
        """Calculate basic statistics"""
        books, users, ratings = data

        total_books = len(books)
        total_users = len(users)
        total_ratings = len(ratings)

        avg_rating = self.calculators.get('average_rating', lambda x: 0.0)(ratings)

        return {
            'total_books': total_books,
            'total_users': total_users,
            'total_ratings': total_ratings,
            'average_rating': avg_rating,
            'books': books,
            'users': users,
            'ratings': ratings
        }

    def _enrich_with_metrics(self, stats: Dict[str, Any]) -> DayReport:
        """Enrich statistics with additional metrics"""
        books = stats['books']
        users = stats['users']
        ratings = stats['ratings']

        # Calculate popular genres
        genre_counter = {}
        for book in books:
            genre_counter[book.genre] = genre_counter.get(book.genre, 0) + 1

        popular_genres = sorted(
            genre_counter.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Calculate active users (simplified)
        user_activity = {}
        for rating in ratings:
            user_activity[rating.user_id] = user_activity.get(rating.user_id, 0) + 1

        active_users = sorted(
            user_activity.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return DayReport(
            date="2024-01-15",  # Fixed for demo
            total_books=stats['total_books'],
            total_users=stats['total_users'],
            total_ratings=stats['total_ratings'],
            average_rating=stats['average_rating'],
            popular_genres=popular_genres,
            active_users=active_users
        )

    def validate_rating(self, rating, books, users, existing_ratings):
        """Validate rating using injected validator"""
        validator = self.validators.get('rating')
        if validator:
            return validator(rating, books, users, existing_ratings)
        return rating

    def get_user_stats(self, user_id: str, books, users, ratings) -> Dict[str, Any]:
        """Get user statistics using composed functions"""
        user_books = self.selectors.get('user_books', lambda *args: [])(user_id, ratings, books)
        user_ratings = self.selectors.get('user_ratings', lambda *args: [])(user_id, ratings)

        return {
            'user_id': user_id,
            'books_rated': len(user_ratings),
            'average_user_rating': self.calculators.get('user_average_rating', lambda x: 0.0)(user_ratings),
            'favorite_genre': self.calculators.get('favorite_genre', lambda x: 'Unknown')(user_books)
        }


class RecoService:
    """
    Recommendation service with dependency injection for pure functions.
    Uses explicit pipe for data transformation pipeline.
    recommend → filter → limit results.
    """

    def __init__(self, recommend: Callable, postfilters: List[Callable]):
        self.recommend = recommend
        self.postfilters = postfilters

    def recommend_top(self, user_id: str, k: int, books, users, ratings) -> List[Recommendation]:
        """Get top-k recommendations with post-filtering using explicit pipe"""
        try:
            # Use pipe to explicitly show the data transformation pipeline
            recommendations = pipe(
                user_id,
                # Step 1: Generate raw recommendations
                lambda uid: self.recommend(uid, ratings, books),
                # Step 2: Apply all post-filters sequentially
                *self.postfilters,
                # Step 3: Format recommendations with metadata
                lambda recs: self._format_recommendations(recs, books),
                # Step 4: Limit to top-k results
                lambda formatted: formatted[:k]
            )
            return recommendations
        except Exception as e:
            print(f"Recommendation error: {e}")
            return []

    def recommend_with_filters(self,
                               user_id: str,
                               k: int,
                               books,
                               users,
                               ratings,
                               custom_filters: List[Callable]) -> List[Recommendation]:
        """Get recommendations with custom filters using pipe"""
        try:
            # Combine default and custom filters
            all_filters = self.postfilters + custom_filters

            # Use pipe for explicit data flow
            recommendations = pipe(
                user_id,
                # Step 1: Generate raw recommendations
                lambda uid: self.recommend(uid, ratings, books),
                # Step 2: Apply all filters (default + custom)
                *all_filters,
                # Step 3: Format recommendations
                lambda recs: self._format_recommendations(recs, books),
                # Step 4: Limit to top-k
                lambda formatted: formatted[:k]
            )
            return recommendations
        except Exception as e:
            print(f"Recommendation with filters error: {e}")
            return []

    def _format_recommendations(self, recommendations, books) -> List[Recommendation]:
        """Format raw recommendations into Recommendation objects"""
        formatted = []
        for book_id, score in recommendations:
            book = next((b for b in books if b.id == book_id), None)
            if book:
                formatted.append(Recommendation(
                    book_id=book_id,
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    score=score,
                    reason=self._generate_reason(book, score)
                ))
        return formatted

    def _generate_reason(self, book, score: float) -> str:
        """Generate reason for recommendation"""
        if score > 0.8:
            return "Highly matches your reading preferences"
        elif score > 0.6:
            return "Matches your favorite genres"
        elif score > 0.4:
            return "Similar to books you've enjoyed"
        else:
            return "Popular among similar readers"


# Pure functions for dependency injection
def simple_recommend(user_id: str, ratings, books, min_rating: int = 4) -> List[Tuple[str, float]]:
    """Simple content-based recommendation"""
    # Get user's highly rated books
    user_ratings = [r for r in ratings if r.user_id == user_id and r.value >= min_rating]

    if not user_ratings:
        # Fallback: return popular books
        book_scores = {}
        for rating in ratings:
            book_scores[rating.book_id] = book_scores.get(rating.book_id, 0) + 1

        popular_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
        # Convert to same format as main algorithm
        return [(book_id, score / max(1, max(book_scores.values()))) for book_id, score in popular_books]

    # Get preferred genres from highly rated books
    preferred_genres = {}
    for rating in user_ratings:
        book = next((b for b in books if b.id == rating.book_id), None)
        if book:
            preferred_genres[book.genre] = preferred_genres.get(book.genre, 0) + rating.value

    # Score books based on genre preference and rating
    recommendations = []
    for book in books:
        # Skip books already rated by user
        if any(r.book_id == book.id for r in ratings if r.user_id == user_id):
            continue

        score = 0.0
        # Genre match
        genre_score = preferred_genres.get(book.genre, 0) / len(user_ratings) if user_ratings else 0
        score += genre_score * 0.7

        # Book rating
        score += (book.rating / 5.0) * 0.3

        recommendations.append((book.id, score))

    return sorted(recommendations, key=lambda x: x[1], reverse=True)


def filter_already_read(recommendations: List[Tuple[str, float]],
                        user_id: str,
                        ratings) -> List[Tuple[str, float]]:
    """Filter out books already read by user"""
    read_books = {r.book_id for r in ratings if r.user_id == user_id}
    return [(book_id, score) for book_id, score in recommendations if book_id not in read_books]


def filter_by_genre(recommendations: List[Tuple[str, float]],
                    allowed_genres: List[str],
                    books) -> List[Tuple[str, float]]:
    """Filter recommendations by allowed genres"""
    allowed_books = {b.id for b in books if b.genre in allowed_genres}
    return [(book_id, score) for book_id, score in recommendations if book_id in allowed_books]


def filter_by_rating(recommendations: List[Tuple[str, float]],
                     min_book_rating: float,
                     books) -> List[Tuple[str, float]]:
    """Filter recommendations by minimum book rating"""
    high_rated_books = {b.id for b in books if b.rating >= min_book_rating}
    return [(book_id, score) for book_id, score in recommendations if book_id in high_rated_books]


def boost_recent_books(recommendations: List[Tuple[str, float]],
                       books,
                       recent_years: int = 5) -> List[Tuple[str, float]]:
    """Boost score of recent books"""
    current_year = 2024  # Fixed for demo
    boosted = []

    for book_id, score in recommendations:
        book = next((b for b in books if b.id == book_id), None)
        if book and (current_year - book.year) <= recent_years:
            # Boost recent books by 20%
            boosted.append((book_id, score * 1.2))
        else:
            boosted.append((book_id, score))

    return sorted(boosted, key=lambda x: x[1], reverse=True)


# Calculator functions
def calculate_average_rating(ratings) -> float:
    """Calculate average rating across all books"""
    if not ratings:
        return 0.0
    return sum(r.value for r in ratings) / len(ratings)


def calculate_user_average_rating(user_ratings) -> float:
    """Calculate average rating for a user"""
    if not user_ratings:
        return 0.0
    return sum(r.value for r in user_ratings) / len(user_ratings)


def calculate_favorite_genre(user_books) -> str:
    """Calculate user's favorite genre"""
    if not user_books:
        return "Unknown"

    genre_count = {}
    for book in user_books:
        genre_count[book.genre] = genre_count.get(book.genre, 0) + 1

    return max(genre_count.items(), key=lambda x: x[1])[0] if genre_count else "Unknown"


# Selector functions
def select_user_books(user_id: str, ratings, books) -> List:
    """Select books rated by user"""
    user_book_ids = {r.book_id for r in ratings if r.user_id == user_id}
    return [b for b in books if b.id in user_book_ids]


def select_user_ratings(user_id: str, ratings) -> List:
    """Select ratings by user"""
    return [r for r in ratings if r.user_id == user_id]


# ==================== Lab 8: Async Recommendation Service ====================

class AsyncRecoService:
    """异步推荐服务 - 集成并行计算和可视化"""

    def __init__(self, async_engine=None):
        from .async_utils import AsyncRecoEngine
        self.async_engine = async_engine or AsyncRecoEngine()
        self.performance_history = []

    async def generate_parallel_report(self, user_ids: List[str], ratings: Tuple[Rating, ...],
                                       books: Tuple[Book, ...], k: int = 5) -> Dict[str, Any]:
        """生成并行推荐报告"""
        start_time = time.time()

        recommendations = await self.async_engine.recommend_batch(user_ids, ratings, books, k)
        metrics = await self.async_engine.get_performance_metrics()
        user_stats = self._calculate_user_stats(user_ids, ratings, books)
        quality_metrics = self._analyze_recommendation_quality(recommendations, books)

        total_time = (time.time() - start_time) * 1000

        report = {
            "timestamp": time.time(),
            "total_processing_time_ms": total_time,
            "users_processed": len(user_ids),
            "recommendations_per_user": k,
            "total_recommendations": sum(len(recs) for recs in recommendations.values()),
            "recommendations": recommendations,
            "performance_metrics": metrics,
            "user_statistics": user_stats,
            "quality_metrics": quality_metrics,
            "system_metrics": {
                "average_recommendation_score": quality_metrics["average_score"],
                "success_rate": quality_metrics["success_rate"],
                "genre_diversity": quality_metrics["genre_diversity"]
            }
        }

        self.performance_history.append(report)
        return report

    def _calculate_user_stats(self, user_ids: List[str], ratings: Tuple[Rating, ...],
                              books: Tuple[Book, ...]) -> Dict[str, Any]:
        """计算用户统计信息"""
        stats = {
            "total_users": len(user_ids),
            "user_activity_levels": {"high": 0, "medium": 0, "low": 0},
            "preferred_genres": {},
            "average_ratings_per_user": 0
        }

        total_ratings = 0
        for user_id in user_ids:
            user_ratings = [r for r in ratings if r.user_id == user_id]
            total_ratings += len(user_ratings)

            if len(user_ratings) >= 5:
                stats["user_activity_levels"]["high"] += 1
            elif len(user_ratings) >= 2:
                stats["user_activity_levels"]["medium"] += 1
            else:
                stats["user_activity_levels"]["low"] += 1

            for rating in user_ratings:
                book = next((b for b in books if b.id == rating.book_id), None)
                if book and rating.value >= 4:
                    stats["preferred_genres"][book.genre] = stats["preferred_genres"].get(book.genre, 0) + 1

        stats["average_ratings_per_user"] = total_ratings / len(user_ids) if user_ids else 0
        stats["preferred_genres"] = dict(sorted(stats["preferred_genres"].items(),
                                                key=lambda x: x[1], reverse=True)[:5])
        return stats

    def _analyze_recommendation_quality(self, recommendations: Dict[str, List['Recommendation']],
                                        books: Tuple[Book, ...]) -> Dict[str, Any]:
        """分析推荐质量"""
        if not recommendations:
            return {"average_score": 0, "success_rate": 0, "genre_diversity": 0, "top_recommended_books": []}

        all_scores = []
        book_recommendation_count = {}
        successful_users = 0

        for user_id, recs in recommendations.items():
            if recs:
                successful_users += 1
                all_scores.extend(rec.score for rec in recs)
                for rec in recs:
                    book_recommendation_count[rec.book_id] = book_recommendation_count.get(rec.book_id, 0) + 1

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        success_rate = successful_users / len(recommendations) if recommendations else 0

        unique_genres = set()
        for recs in recommendations.values():
            for rec in recs:
                unique_genres.add(rec.genre)

        top_books = sorted(book_recommendation_count.items(), key=lambda x: x[1], reverse=True)[:5]
        top_books_with_titles = []

        for book_id, count in top_books:
            book = next((b for b in books if b.id == book_id), None)
            if book:
                top_books_with_titles.append({
                    "title": book.title, "author": book.author,
                    "genre": book.genre, "recommendation_count": count
                })

        return {
            "average_score": avg_score,
            "success_rate": success_rate,
            "genre_diversity": len(unique_genres),
            "top_recommended_books": top_books_with_titles
        }

    def get_performance_history(self) -> List[Dict[str, Any]]:
        return self.performance_history.copy()

    def clear_history(self):
        self.performance_history.clear()