import pytest
import time
from core.events import Event, EventBus, EventHandlers
from core.domain import Book, User, Rating


@pytest.fixture
def sample_books():
    """Fixture providing sample book data for testing"""
    return [
        Book("1", "Test Book 1", "Author 1", "Fiction", 2020, 4.5),
        Book("2", "Test Book 2", "Author 2", "Science", 2021, 4.2),
    ]


@pytest.fixture
def sample_users():
    """Fixture providing sample user data for testing"""
    return [
        User("u1", "Test User 1"),
        User("u2", "Test User 2"),
    ]


@pytest.fixture
def sample_ratings():
    """Fixture providing sample rating data for testing"""
    return [
        Rating("u1", "1", 5),
        Rating("u2", "2", 4),
    ]


@pytest.fixture
def event_bus():
    """Fixture providing EventBus instance"""
    return EventBus()


@pytest.fixture
def event_handlers(sample_books, sample_users, sample_ratings):
    """Fixture providing EventHandlers instance with sample data"""
    return EventHandlers(sample_books, sample_users, sample_ratings)


def test_event_bus_subscription_workflow(event_bus):
    """Test complete event bus subscription and publishing workflow"""
    received_events = []

    def event_handler(event):
        received_events.append(event)

    # Subscribe handler to event type
    event_bus.subscribe("TEST_EVENT", event_handler)

    # Publish event and verify delivery
    test_payload = {"message": "test_data", "value": 42}
    event_bus.publish("TEST_EVENT", test_payload)

    # Verify event was received with correct data
    assert len(received_events) == 1
    assert received_events[0].name == "TEST_EVENT"
    assert received_events[0].payload["message"] == "test_data"
    assert received_events[0].payload["value"] == 42


def test_multiple_handlers_same_event(event_bus):
    """Test that multiple handlers can subscribe to same event type"""
    handler1_calls = []
    handler2_calls = []

    def handler1(event):
        handler1_calls.append(event)

    def handler2(event):
        handler2_calls.append(event)

    # Subscribe both handlers to same event
    event_bus.subscribe("SHARED_EVENT", handler1)
    event_bus.subscribe("SHARED_EVENT", handler2)

    # Publish single event
    event_bus.publish("SHARED_EVENT", {"data": "shared"})

    # Verify both handlers were called
    assert len(handler1_calls) == 1
    assert len(handler2_calls) == 1
    assert handler1_calls[0].payload["data"] == "shared"
    assert handler2_calls[0].payload["data"] == "shared"


def test_rating_event_updates_dashboards(event_handlers, sample_books):
    """Test that rating events properly update all relevant dashboards"""
    rating_event = Event(
        "RATING_ADDED",
        {"book_id": "1", "user_id": "u1", "rating_value": 5},
        time.time()
    )

    # Test genre tracking update
    genre_results = event_handlers.update_weekly_top_genres(rating_event)
    assert "Fiction" in genre_results
    assert genre_results["Fiction"] == 1

    # Test popularity scoring update
    popularity_results = event_handlers.update_popular_books(rating_event)
    assert popularity_results["1"] == 2  # +2 points for rating

    # Test user activity tracking update
    activity_results = event_handlers.update_user_activity(rating_event)
    assert activity_results["u1"]["rating_count"] == 1


def test_loan_event_tracking(event_handlers):
    """Test that loan events are properly tracked in the system"""
    loan_event = Event(
        "LOAN_ISSUED",
        {
            "user_id": "u1",
            "book_id": "1",
            "loan_date": "2024-01-15",
            "due_date": "2024-01-29"
        },
        time.time()
    )

    # Test recent loans tracking
    recent_loans = event_handlers.update_recent_loans(loan_event)
    assert len(recent_loans) == 1
    assert recent_loans[0]["user_id"] == "u1"
    assert recent_loans[0]["book_id"] == "1"

    # Test popularity scoring for loans
    popularity_results = event_handlers.update_popular_books(loan_event)
    assert popularity_results["1"] == 1  # +1 point for loan


def test_event_history_persistence(event_bus):
    """Test that event bus maintains complete history of all published events"""
    # Publish multiple events of different types
    event_bus.publish("USER_LOGIN", {"user_id": "u1", "action": "login"})
    event_bus.publish("BOOK_VIEW", {"book_id": "1", "user_id": "u1"})
    event_bus.publish("RATING_ADDED", {"book_id": "1", "rating": 5})

    # Retrieve event history
    history = event_bus.get_event_history()

    # Verify history contains all events in correct order
    assert len(history) == 3
    assert history[0].name == "USER_LOGIN"
    assert history[1].name == "BOOK_VIEW"
    assert history[2].name == "RATING_ADDED"

    # Verify event payloads are preserved
    assert history[0].payload["action"] == "login"
    assert history[1].payload["book_id"] == "1"
    assert history[2].payload["rating"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ==================== Lab 8扩展测试：事件系统集成 ====================

def test_event_system_integration_with_async():
    """测试事件系统与异步计算的集成"""
    from core.events import EventBus, Event

    event_bus = EventBus()
    events_received = []

    def async_completion_handler(event):
        events_received.append(event)

    # 订阅异步完成事件
    event_bus.subscribe("ASYNC_RECOMMENDATIONS_COMPLETE", async_completion_handler)

    # 模拟异步计算完成事件
    test_payload = {
        "users_processed": 15,
        "processing_time_ms": 2450,
        "success_rate": 0.93
    }

    event_bus.publish("ASYNC_RECOMMENDATIONS_COMPLETE", test_payload)

    # 验证事件处理
    assert len(events_received) == 1
    assert events_received[0].name == "ASYNC_RECOMMENDATIONS_COMPLETE"
    assert events_received[0].payload["users_processed"] == 15


def test_real_time_dashboard_updates():
    """测试实时仪表板更新"""
    from core.events import EventHandlers
    from core.domain import Book, User, Rating

    # 创建测试数据
    books = [Book("1", "Test Book", "Author", "Fiction", 2020, 4.5)]
    users = [User("u1", "Test User")]
    ratings = [Rating("u1", "1", 5)]

    handlers = EventHandlers(books, users, ratings)

    # 模拟多个评分事件
    from core.events import Event
    import time

    for i in range(5):
        event = Event(
            "RATING_ADDED",
            {"book_id": "1", "user_id": "u1", "rating_value": 5},
            time.time()
        )
        handlers.update_weekly_top_genres(event)
        handlers.update_popular_books(event)

    # 验证仪表板数据更新
    top_genres = handlers.update_weekly_top_genres(Event("DUMMY", {}, time.time()))
    popular_books = handlers.update_popular_books(Event("DUMMY", {}, time.time()))

    assert "Fiction" in top_genres
    assert top_genres["Fiction"] == 5  # 5个评分事件
    assert "1" in popular_books
    assert popular_books["1"] == 10  # 5个评分 * 2分每个