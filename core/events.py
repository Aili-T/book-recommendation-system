from typing import NamedTuple, Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from functools import wraps
import time


class Event(NamedTuple):
    name: str
    payload: Dict[str, Any]
    timestamp: float


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._event_history: List[Event] = []

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe handler to event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Unsubscribe handler from event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]

    def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish event to all subscribers"""
        event = Event(event_type, payload, time.time())
        self._event_history.append(event)

        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")

    def get_event_history(self) -> List[Event]:
        """Get all published events"""
        return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()


# Global event bus instance
event_bus = EventBus()


# Event payload schemas
@dataclass(frozen=True)
class RatingAddedPayload:
    user_id: str
    book_id: str
    rating_value: int
    timestamp: float


@dataclass(frozen=True)
class ReviewAddedPayload:
    user_id: str
    book_id: str
    review_text: str
    timestamp: float


@dataclass(frozen=True)
class LoanIssuedPayload:
    user_id: str
    book_id: str
    loan_date: str
    due_date: str


@dataclass(frozen=True)
class LoanReturnedPayload:
    user_id: str
    book_id: str
    return_date: str
    loan_duration_days: int


# Pure event handlers for state transformation
class EventHandlers:
    def __init__(self, books, users, ratings):
        self.books = books
        self.users = users
        self.ratings = ratings
        self.state = {
            'weekly_top_genres': {},
            'new_arrivals': [],
            'user_activity': {},
            'popular_books': {},
            'recent_loans': []
        }

    # 纯函数处理事件，返回新状态
    def update_weekly_top_genres(self, event: Event) -> Dict[str, Any]:
        """Update weekly top genres based on ratings"""
        if event.name == "RATING_ADDED":
            book_id = event.payload.get('book_id')
            book = next((b for b in self.books if b.id == book_id), None)

            if book:
                genre = book.genre
                self.state['weekly_top_genres'][genre] = \
                    self.state['weekly_top_genres'].get(genre, 0) + 1

        # Sort by count descending
        sorted_genres = sorted(
            self.state['weekly_top_genres'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        return dict(sorted_genres[:5])

    def update_new_arrivals(self, event: Event) -> List[Dict[str, Any]]:
        """Track newly added books (simulated)"""
        if event.name == "BOOK_ADDED":
            book_data = event.payload
            self.state['new_arrivals'].append({
                'title': book_data.get('title', ''),
                'author': book_data.get('author', ''),
                'genre': book_data.get('genre', ''),
                'timestamp': event.timestamp
            })

        # Keep only last 10 arrivals
        self.state['new_arrivals'] = sorted(
            self.state['new_arrivals'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]

        return self.state['new_arrivals']

    def update_user_activity(self, event: Event) -> Dict[str, Any]:
        """Track user activity metrics"""
        user_id = event.payload.get('user_id')

        if user_id:
            user_activity = self.state['user_activity'].get(user_id, {
                'rating_count': 0,
                'review_count': 0,
                'loan_count': 0,
                'last_activity': 0
            })

            if event.name == "RATING_ADDED":
                user_activity['rating_count'] += 1
            elif event.name == "REVIEW_ADDED":
                user_activity['review_count'] += 1
            elif event.name == "LOAN_ISSUED":
                user_activity['loan_count'] += 1

            user_activity['last_activity'] = event.timestamp
            self.state['user_activity'][user_id] = user_activity

        return self.state['user_activity']

    def update_popular_books(self, event: Event) -> Dict[str, Any]:
        """Update book popularity scores"""
        if event.name in ["RATING_ADDED", "LOAN_ISSUED"]:
            book_id = event.payload.get('book_id')
            if book_id:
                current_score = self.state['popular_books'].get(book_id, 0)

                if event.name == "RATING_ADDED":
                    self.state['popular_books'][book_id] = current_score + 2
                elif event.name == "LOAN_ISSUED":
                    self.state['popular_books'][book_id] = current_score + 1

        return dict(sorted(
            self.state['popular_books'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])

    def update_recent_loans(self, event: Event) -> List[Dict[str, Any]]:
        """Track recent loan activity"""
        if event.name == "LOAN_ISSUED":
            loan_data = {
                'user_id': event.payload.get('user_id'),
                'book_id': event.payload.get('book_id'),
                'loan_date': event.payload.get('loan_date'),
                'timestamp': event.timestamp
            }
            self.state['recent_loans'].append(loan_data)

        # Keep only last 15 loans
        self.state['recent_loans'] = sorted(
            self.state['recent_loans'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:15]

        return self.state['recent_loans']


# Decorator for pure event handlers
def pure_handler(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, event: Event) -> Any:
        # Ensure no side effects by working on copied state
        original_state = self.state.copy()
        try:
            result = func(self, event)
            return result
        finally:
            # Restore original state to maintain purity
            self.state = original_state

    return wrapper