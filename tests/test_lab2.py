from dataclasses import dataclass
from typing import List, Optional, Tuple



@dataclass
class Tag:
    id: str
    name: str
    parent_id: Optional[str] = None
    children: List['Tag'] = None


@dataclass(frozen=True)
class Book:
    id: str
    title: str
    author: str
    genre: str
    year: int
    rating: float


def create_genre_filter(genre: str):
    """Closure: Type Filter Generator"""

    def genre_filter(book):
        return book.genre.lower() == genre.lower()

    return genre_filter


def create_rating_filter(min_rating: float = 0.0):


    def rating_filter(book):
        return book.rating >= min_rating

    return rating_filter


def combine_filters(*filters):
    """Higher-order functions: combining multiple filters"""

    def combined_filter(book):
        return all(filter_func(book) for filter_func in filters)

    return combined_filter


def find_tag_by_name(tag: Tag, name: str) -> Optional[Tag]:
    """Recursive Algorithm 1: Tag Search"""
    if tag.name.lower() == name.lower():
        return tag
    if tag.children:
        for child in tag.children:
            result = find_tag_by_name(child, name)
            if result:
                return result
    return None


def find_related_books(book: Book, all_books: Tuple[Book, ...]) -> Tuple[Book, ...]:


    def find_similar(current_book, visited):
        if current_book.id in visited:
            return []
        visited.add(current_book.id)

        similar = []
        for other_book in all_books:
            if (other_book.id not in visited and
                    other_book.genre == current_book.genre and
                    other_book.id != book.id):
                similar.append(other_book)
                # 递归查找更多相关书籍
                visited.add(other_book.id)
                more_similar = find_similar(other_book, visited)
                similar.extend(more_similar)
        return similar

    return tuple(find_similar(book, set()))


def run_all_tests():
    """five text"""
    print("🎯 Running Lab 2 - 5 Core Tests\n")


    books = (
        Book("1", "Dune", "Frank Herbert", "Sci-Fi", 1965, 4.8),
        Book("2", "The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 4.9),
        Book("3", "Project Hail Mary", "Andy Weir", "Sci-Fi", 2021, 4.5),
        Book("4", "Foundation", "Isaac Asimov", "Sci-Fi", 1951, 4.6),
    )

    root = Tag("1", "Literature")
    fiction = Tag("2", "Fiction")
    scifi = Tag("3", "Sci-Fi")
    fantasy = Tag("4", "Fantasy")

    fiction.children = [scifi, fantasy]
    root.children = [fiction]

    print("1. 🔄 Testing Closure Filters")
    sci_fi_filter = create_genre_filter("Sci-Fi")
    sci_fi_books = tuple(filter(sci_fi_filter, books))
    assert len(sci_fi_books) == 3, f"Expected 3 Sci-Fi books, got {len(sci_fi_books)}"
    print("   ✅ PASS: Closure filters work correctly")

    print("2. 🔄 Testing Filter Combination")
    genre_filter = create_genre_filter("Sci-Fi")
    rating_filter = create_rating_filter(4.6)
    combined = combine_filters(genre_filter, rating_filter)
    filtered_books = tuple(filter(combined, books))
    assert len(filtered_books) == 2, f"Expected 2 books, got {len(filtered_books)}"
    print("   ✅ PASS: Filter combination works correctly")

    # Test 3:Recursive tag search
    print("3. 🔄 Testing Recursive Tag Search")
    found_tag = find_tag_by_name(root, "Sci-Fi")
    assert found_tag is not None, "Should find Sci-Fi tag"
    assert found_tag.name == "Sci-Fi", f"Found wrong tag: {found_tag.name}"
    print("   ✅ PASS: Recursive tag search works correctly")

    # Test 4:Books on recursion
    print("4. 🔄 Testing Recursive Related Books")
    target_book = books[0]  # Dune (Sci-Fi)
    related = find_related_books(target_book, books)
    assert len(related) == 2, f"Expected 2 related books, got {len(related)}"
    assert all(b.genre == "Sci-Fi" for b in related), "All related books should be Sci-Fi"
    print("   ✅ PASS: Recursive related books works correctly")

    # Test 5: Lambda expression
    print("5. 🔄 Testing Lambda Expressions")
    high_rated_sci_fi = list(filter(
        lambda b: b.genre == "Sci-Fi" and b.rating >= 4.6,
        books
    ))
    assert len(high_rated_sci_fi) == 2, "Lambda filter should find 2 books"
    print("   ✅ PASS: Lambda expressions work correctly")

    print("\n🎉 SUCCESS! All 5 Lab 2 tests passed!")
    print("\n📋 Lab 2 Requirements Verified:")
    print("   ✅ Closures and lambda expressions")
    print("   ✅ Configurator closures (filter generators)")
    print("   ✅ 2 recursive algorithms (tag search + related books)")
    print("   ✅ Higher-order functions (filter combination)")
    print("   ✅ Functional programming style")


if __name__ == "__main__":
    run_all_tests()