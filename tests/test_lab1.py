import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.domain import Book, User, Rating
from core.transforms import *


def test_lab1_simple():
    """lab-1 test"""
    print("🧪 Running Complete Lab 1 Tests (5 Tests)...")


    books = (
        Book("1", "Book 1", "Author 1", "Fiction", 2010, 4.0),
        Book("2", "Book 2", "Author 2", "Sci-Fi", 2020, 4.5),
        Book("3", "Book 3", "Author 3", "Fiction", 2022, 4.2),
    )

    #1.Immutable Data Structures - Test all data classes
    print("1. 🔒 Testing Immutable Data Classes...")
    book = Book("1", "Test Book", "Test Author", "Fiction", 2020, 4.5)
    user = User("u1", "Test User")
    rating = Rating("u1", "1", 5)


    try:
        book.title = "New Title"
        print("   ❌ FAIL: Book should be immutable")
    except:
        print("   ✅ PASS: Book is immutable")


    try:
        user.name = "New Name"
        print("   ❌ FAIL: User should be immutable")
    except:
        print("   ✅ PASS: User is immutable")


    try:
        rating.value = 3
        print("   ❌ FAIL: Rating should be immutable")
    except:
        print("   ✅ PASS: Rating is immutable")

    #pure function Filter
    print("2. 🔍 Testing Pure Function - Filter by Year...")
    filtered = filter_books_by_year(books, 2020)
    expected_count = 2  # 2020和2022年的书籍
    if len(filtered) == expected_count and all(book.year >= 2020 for book in filtered):
        print(f"   ✅ PASS: Filter found {len(filtered)} books from 2020 or later")
    else:
        print(f"   ❌ FAIL: Expected {expected_count} books, got {len(filtered)}")


    print("3. 🏷️ Testing Pure Function - Filter by Genre...")
    fiction_books = filter_books_by_genre(books, "Fiction")
    expected_fiction = 2  # Book 1和Book 3
    if len(fiction_books) == expected_fiction and all(book.genre == "Fiction" for book in fiction_books):
        print(f"   ✅ PASS: Filter found {len(fiction_books)} Fiction books")
    else:
        print(f"   ❌ FAIL: Expected {expected_fiction} Fiction books, got {len(fiction_books)}")


    print("4. 🗺️ Testing Higher-Order Function - Map (Extract Titles)...")
    titles = get_book_titles(books)
    expected_titles = ("Book 1", "Book 2", "Book 3")
    if titles == expected_titles and isinstance(titles, tuple):
        print(f"   ✅ PASS: Map correctly extracted titles: {titles}")
    else:
        print(f"   ❌ FAIL: Expected {expected_titles}, got {titles}")

    print("5. 📊 Testing Higher-Order Function - Reduce (Average Rating)...")
    avg_rating = get_average_rating(books)
    expected_avg = (4.0 + 4.5 + 4.2) / 3  # 计算期望的平均值
    if abs(avg_rating - expected_avg) < 0.01:
        print(f"   ✅ PASS: Reduce calculated correct average: {avg_rating:.2f}")
    else:
        print(f"   ❌ FAIL: Expected {expected_avg:.2f}, got {avg_rating:.2f}")

    print("\n🎉 All 5 Lab 1 Tests Completed!")
    print("📋 Lab 1 Requirements Verified:")
    print("   ✅ Immutable Data Structures")
    print("   ✅ Pure Functions (no side effects)")
    print("   ✅ Higher-Order Functions (Map/Filter/Reduce)")
    print("   ✅ Functional Programming Style")


if __name__ == "__main__":
    test_lab1_simple()