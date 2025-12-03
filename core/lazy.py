# core/lazy.py
import heapq
from typing import Iterable, Iterator, Tuple, List, Callable, Any
from typing import Iterable, Iterator, Tuple, Callable, List, Optional
from dataclasses import dataclass
import heapq

try:
    from core.domain import Book
    from core.recursion import Tag
except ImportError:
    # Fallback definitions
    @dataclass(frozen=True)
    class Book:
        id: str
        title: str
        author: str
        genre: str
        year: int
        rating: float


    @dataclass
    class Tag:
        id: str
        name: str
        parent_id: Optional[str] = None
        children: List['Tag'] = None


def iter_books_by_taxonomy(books: Iterable[Book],
                           genres_tree: Tag,
                           tags_tree: Tag,
                           pred: Callable[[Book, Tag, Tag], bool]) -> Iterator[Book]:
    """
    Lazy iterator for books filtered by taxonomy with custom predicate.

    Args:
        books: Iterable of books
        genres_tree: Genre taxonomy hierarchy
        tags_tree: Tags taxonomy hierarchy
        pred: Predicate function (book, genre_tag, book_tag) -> bool

    Yields:
        Books that satisfy the predicate condition
    """

    # Flatten taxonomies for easy lookup
    def flatten_tags(tag: Tag) -> List[Tag]:
        tags = [tag]
        if tag.children:
            for child in tag.children:
                tags.extend(flatten_tags(child))
        return tags

    all_genres = flatten_tags(genres_tree)
    all_tags = flatten_tags(tags_tree)

    for book in books:
        # Find matching genre tag
        genre_tag = next((tag for tag in all_genres if tag.name.lower() == book.genre.lower()), None)

        # Find matching book tag (simplified - using author as tag)
        book_tag = next((tag for tag in all_tags if tag.name.lower() in book.author.lower()), None)

        if pred(book, genre_tag, book_tag):
            yield book


def lazy_top_k(stream: Iterable[Tuple[str, float]], k: int) -> Iterator[Tuple[str, float]]:
    """
    Streaming top-K: maintain the k best items as ratings/scores come in.

    Args:
        stream: Iterable of (item_id, score) tuples
        k: Number of top items to maintain

    Yields:
        Current top-k items after processing each element (for demonstration)
        Final result is the last yielded value
    """
    heap = []  # min-heap for top-k items

    for item_id, score in stream:
        # Use negative score for min-heap behavior
        if len(heap) < k:
            heapq.heappush(heap, (score, item_id))
        else:
            # Replace the smallest if current is larger
            if score > heap[0][0]:
                heapq.heappushpop(heap, (score, item_id))

        # Yield current state for demonstration
        current_top = sorted(heap, reverse=True)
        yield [(item_id, score) for score, item_id in current_top]


def lazy_book_recommendations(books: Iterable[Book],
                              user_profile: dict,
                              k: int = 10) -> Iterator[Tuple[Book, float]]:
    """
    Lazy book recommendation generator.

    Args:
        books: Iterable of books
        user_profile: User preferences dictionary
        k: Number of recommendations to generate

    Yields:
        (book, score) tuples for recommended books
    """
    scored_books = []

    for book in books:
        # Calculate recommendation score (simplified)
        score = 0.0

        # Genre match
        if 'preferred_genres' in user_profile and book.genre in user_profile['preferred_genres']:
            score += 2.0

        # Author match
        if 'preferred_authors' in user_profile and book.author in user_profile['preferred_authors']:
            score += 1.5

        # Rating bonus
        score += book.rating * 0.1

        scored_books.append((book, score))

    # Sort and yield top-k
    scored_books.sort(key=lambda x: x[1], reverse=True)

    for i, (book, score) in enumerate(scored_books[:k]):
        yield book, score


def lazy_book_search(books: Iterable[Book],
                     search_terms: List[str],
                     min_rating: float = 0.0) -> Iterator[Book]:
    """
    Lazy book search with multiple search terms.

    Args:
        books: Iterable of books
        search_terms: List of terms to search in title/author
        min_rating: Minimum book rating

    Yields:
        Books matching search criteria
    """
    for book in books:
        if book.rating < min_rating:
            continue

        # Check if any search term matches title or author
        matches = any(
            term.lower() in book.title.lower() or
            term.lower() in book.author.lower()
            for term in search_terms
        )

        if matches:
            yield book


def batch_process_books(books: Iterable[Book],
                        batch_size: int = 5,
                        process_func: Callable[[List[Book]], any] = None) -> Iterator[any]:
    """
    Process books in batches lazily.

    Args:
        books: Iterable of books
        batch_size: Number of books per batch
        process_func: Function to process each batch

    Yields:
        Results from processing each batch
    """
    batch = []

    for book in books:
        batch.append(book)

        if len(batch) >= batch_size:
            result = process_func(batch) if process_func else batch
            yield result
            batch = []

    # Process remaining books
    if batch:
        result = process_func(batch) if process_func else batch
        yield result


# Test functions
def test_lazy_top_k():
    """Test the lazy top-k functionality"""
    print("🧪 Testing lazy_top_k...")

    # Test data
    stream = [("book1", 4.5), ("book2", 3.8), ("book3", 4.9),
              ("book4", 4.2), ("book5", 4.7), ("book6", 3.5)]

    results = list(lazy_top_k(stream, 3))
    final_result = results[-1]

    print(f"Final top-3: {final_result}")
    assert len(final_result) == 3
    assert final_result[0][1] == 4.9  # Highest score
    print("✅ lazy_top_k test passed!")


def test_lazy_book_search():
    """Test lazy book search"""
    print("🧪 Testing lazy_book_search...")

    # Create test books
    test_books = [
        Book("1", "Python Programming", "John Doe", "Education", 2020, 4.5),
        Book("2", "Advanced Python", "Jane Smith", "Education", 2021, 4.7),
        Book("3", "Java Basics", "John Doe", "Education", 2019, 3.8),
    ]

    results = list(lazy_book_search(test_books, ["python"], 4.0))

    print(f"Found {len(results)} books")
    assert len(results) == 2
    assert all("python" in book.title.lower() for book in results)
    print("✅ lazy_book_search test passed!")


if __name__ == "__main__":
    # Run tests
    test_lazy_top_k()
    test_lazy_book_search()
    print("🎉 All lazy computation tests completed!")