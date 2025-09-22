import streamlit as st
import sys
import os
from dataclasses import dataclass
from typing import List, Optional


# 临时在main.py中定义Tag类
@dataclass
class Tag:
    id: str
    name: str
    parent_id: Optional[str] = None
    children: List['Tag'] = None


# 然后导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.domain import Book, User, Rating
    from core.transforms import *
    from core.filters import *
except ImportError as e:
    st.error(f"Import Error: {e}")


    # 如果其他导入也失败，在这里定义所有必要的类
    @dataclass(frozen=True)
    class Book:
        id: str
        title: str
        author: str
        genre: str
        year: int
        rating: float


    @dataclass(frozen=True)
    class User:
        id: str
        name: str


    @dataclass(frozen=True)
    class Rating:
        user_id: str
        book_id: str
        value: int


# Create sample data
def create_sample_data():
    sample_books = (
        Book("1", "The Path of Abai", "Mukhtar Auezov", "Classic", 1942, 4.7),
        Book("2", "Dune", "Frank Herbert", "Sci-Fi", 1965, 4.8),
        Book("3", "The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 4.9),
        Book("4", "Project Hail Mary", "Andy Weir", "Sci-Fi", 2021, 4.5),
        Book("5", "World History", "Multiple Authors", "History", 2018, 4.5),
        Book("6", "Python Programming", "John Smith", "Computer Science", 2020, 4.3),
        Book("7", "Machine Learning", "Jane Doe", "Computer Science", 2019, 4.6),
    )

    sample_users = (
        User("u1", "Alice"),
        User("u2", "Bob"),
        User("u3", "Charlie"),
    )

    sample_ratings = (
        Rating("u1", "1", 5),
        Rating("u2", "1", 4),
        Rating("u1", "2", 5),
        Rating("u3", "2", 4),
        Rating("u1", "3", 5),
    )

    return sample_books, sample_users, sample_ratings


# 递归函数定义
def find_tag_by_name_simple(tags, name: str):
    """简化版标签查找"""
    for tag in tags:
        if tag.name.lower() == name.lower():
            return tag
        if tag.children:  # 直接检查children
            result = find_tag_by_name_simple(tag.children, name)
            if result:
                return result
    return None


def build_genre_hierarchy_simple(books):
    """简化版构建类型层次"""
    genres = set(book.genre for book in books)

    fiction_tags = []
    nonfiction_tags = []

    for genre in genres:
        if genre in ["Sci-Fi", "Fantasy", "Classic"]:
            fiction_tags.append(Tag(f"sub_{genre}", genre, None, []))
        else:
            nonfiction_tags.append(Tag(f"sub_{genre}", genre, None, []))

    fiction = Tag("cat_fiction", "Fiction", None, fiction_tags)
    nonfiction = Tag("cat_nonfiction", "Non-Fiction", None, nonfiction_tags)

    return [fiction, nonfiction]


def display_hierarchy_simple(tags, level=0):
    """简化版显示层次结构"""
    for tag in tags:
        indent = "&nbsp;" * (level * 4)
        st.markdown(f"{indent}📁 **{tag.name}**")
        if tag.children:
            display_hierarchy_simple(tag.children, level + 1)


# 简化的过滤器函数（如果在core.filters中找不到）
def create_genre_filter(genre: str):
    """创建类型过滤器"""

    def genre_filter(book):
        return book.genre.lower() == genre.lower()

    return genre_filter


def create_rating_filter(min_rating: float = 0.0, max_rating: float = 5.0):
    """创建评分过滤器"""

    def rating_filter(book):
        return min_rating <= book.rating <= max_rating

    return rating_filter


def create_advanced_search(genres=None, min_rating=0, start_year=1900, end_year=2025):
    """创建高级搜索"""

    def search_function(books):
        filters = []

        if genres:
            genre_filter = lambda book: any(genre.lower() == book.genre.lower() for genre in genres)
            filters.append(genre_filter)

        if min_rating > 0:
            rating_filter = create_rating_filter(min_rating)
            filters.append(rating_filter)

        year_filter = lambda book: start_year <= book.year <= end_year
        filters.append(year_filter)

        def combined_filter(book):
            return all(f(book) for f in filters)

        return tuple(filter(combined_filter, books))

    return search_function


# Page configuration
st.set_page_config(page_title="Book Recommendation System", layout="wide")

# Sidebar menu
st.sidebar.title("Navigation Menu")
menu = st.sidebar.radio("Select Page", ["Overview", "Data", "Functional Core", "Lambdas & Closures", "Recursion"])

# Load data
books_data, users_data, ratings_data = create_sample_data()

# Overview Page
if menu == "Overview":
    st.title("📊 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Books", len(books_data))
    with col2:
        st.metric("Total Users", len(users_data))
    with col3:
        st.metric("Total Ratings", len(ratings_data))
    with col4:
        # 简化的平均评分计算
        if books_data:
            avg_rating = sum(book.rating for book in books_data) / len(books_data)
        else:
            avg_rating = 0
        st.metric("Average Rating", f"{avg_rating:.2f}")

    st.subheader("Book Catalog")
    for book in books_data:
        st.write(f"- **{book.title}** by {book.author} ({book.year}) - ⭐ {book.rating}")

# Data Page
elif menu == "Data":
    st.title("📁 Data Management")

    st.success("✅ Sample data loaded successfully!")
    st.write(f"**Statistics:** {len(books_data)} books, {len(users_data)} users, {len(ratings_data)} ratings")

    st.subheader("Books Data")
    book_data_table = []
    for book in books_data:
        book_data_table.append({
            "ID": book.id,
            "Title": book.title,
            "Author": book.author,
            "Genre": book.genre,
            "Year": book.year,
            "Rating": book.rating
        })
    st.table(book_data_table)

# Functional Core Page
elif menu == "Functional Core":
    st.title("🔧 Functional Core Demo")

    st.subheader("Higher-Order Functions Demonstration")

    st.write("**1. Filter Function: Books published after 2000**")
    recent_books = tuple(filter(lambda b: b.year >= 2000, books_data))
    st.write("Results:", [b.title for b in recent_books])

    st.write("**2. Map Function: Extract book titles and years**")
    book_info = list(map(lambda b: (b.title, b.year), books_data))
    st.write("Results:", book_info)

    st.write("**3. Reduce Function: Calculate average book rating**")
    if books_data:
        avg_rating = sum(book.rating for book in books_data) / len(books_data)
    else:
        avg_rating = 0
    st.write(f"Result: {avg_rating:.2f}")

    st.subheader("Interactive Filtering")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Filter by Genre**")
        selected_genre = st.selectbox("Select a genre:",
                                      ["Sci-Fi", "Fantasy", "Classic", "History", "Computer Science"])
        genre_books = tuple(filter(lambda b: b.genre == selected_genre, books_data))
        st.write(f"**{selected_genre} Books ({len(genre_books)} found):**")
        for book in genre_books:
            st.write(f"- {book.title} ({book.year}) - ⭐ {book.rating}")

    with col2:
        st.write("**Filter by Year**")
        min_year = st.slider("Minimum publication year:", 1900, 2025, 2000)
        filtered_books = tuple(filter(lambda b: b.year >= min_year, books_data))
        st.write(f"**Books published after {min_year} ({len(filtered_books)} found):**")
        for book in filtered_books:
            st.write(f"- {book.title} - ⭐ {book.rating}")

# Lambdas & Closures Page
elif menu == "Lambdas & Closures":
    st.title("λ Lambdas & Closures Demo")

    st.subheader("Closure-based Filter Generators")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Genre Filter Closure**")
        selected_genre = st.selectbox("Choose genre for closure:",
                                      ["Sci-Fi", "Fantasy", "Classic"])
        genre_filter = create_genre_filter(selected_genre)
        filtered_books = tuple(filter(genre_filter, books_data))
        st.write(f"Books in {selected_genre}: {len(filtered_books)}")
        for book in filtered_books:
            st.write(f"- {book.title}")

    with col2:
        st.write("**Rating Filter Closure**")
        min_rating = st.slider("Minimum rating:", 3.0, 5.0, 4.0, 0.1)
        rating_filter = create_rating_filter(min_rating)
        high_rated_books = tuple(filter(rating_filter, books_data))
        st.write(f"High-rated books (≥{min_rating}): {len(high_rated_books)}")
        for book in high_rated_books:
            st.write(f"- {book.title} ⭐{book.rating}")

    st.subheader("Advanced Search with Combined Closures")

    advanced_col1, advanced_col2 = st.columns(2)

    with advanced_col1:
        selected_genres = st.multiselect("Select genres:",
                                         ["Sci-Fi", "Fantasy", "Classic", "History", "Computer Science"])
        min_rating_adv = st.slider("Min rating:", 0.0, 5.0, 4.0, 0.1)

    with advanced_col2:
        start_year = st.slider("Start year:", 1900, 2025, 1950)
        end_year = st.slider("End year:", 1900, 2025, 2025)

    if st.button("Apply Advanced Search"):
        search_func = create_advanced_search(
            genres=selected_genres,
            min_rating=min_rating_adv,
            start_year=start_year,
            end_year=end_year
        )
        results = search_func(books_data)
        st.write(f"**Advanced Search Results: {len(results)} books found**")
        for book in results:
            st.write(f"- {book.title} by {book.author} ({book.year}) - ⭐{book.rating}")

# Recursion Page
elif menu == "Recursion":
    st.title("🔄 Recursion Algorithms Demo")

    st.subheader("Genre Hierarchy and Related Books")

    genre_hierarchy = build_genre_hierarchy_simple(books_data)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Genre Hierarchy Tree**")
        display_hierarchy_simple(genre_hierarchy)

    with col2:
        st.write("**Find Related Books**")
        selected_book = st.selectbox("Select a book to find related ones:",
                                     [f"{b.title} by {b.author}" for b in books_data])

        if selected_book:
            book_index = [f"{b.title} by {b.author}" for b in books_data].index(selected_book)
            selected_book_obj = books_data[book_index]

            if st.button("Find Related Books"):
                related_books = []
                for book in books_data:
                    if book.id != selected_book_obj.id and book.genre == selected_book_obj.genre:
                        related_books.append(book)

                st.write(f"**Found {len(related_books)} related books:**")
                for book in related_books:
                    st.write(f"- {book.title} by {book.author} ({book.genre}) ⭐{book.rating}")

    st.subheader("Tag Search Recursion")

    # 创建示例标签结构
    root_tag = Tag("1", "Literature", None, [])
    fiction_tag = Tag("2", "Fiction", None, [])
    scifi_tag = Tag("3", "Sci-Fi", None, [])
    fantasy_tag = Tag("4", "Fantasy", None, [])

    fiction_tag.children.extend([scifi_tag, fantasy_tag])
    root_tag.children.append(fiction_tag)

    search_tag = st.text_input("Search for tag in hierarchy:", "Sci-Fi")

    if st.button("Search Tag"):
        found_tag = find_tag_by_name_simple([root_tag], search_tag)
        if found_tag:
            st.success(f"✅ Found tag: {found_tag.name}")
            st.write(f"Tag ID: {found_tag.id}")
        else:
            st.error(f"❌ Tag '{search_tag}' not found")

# Footer information
st.sidebar.markdown("---")
st.sidebar.info("""
**Lab 1 Completed:** Pure Functions + Immutability + Higher-Order Functions  
**Lab 2 Completed:** Lambdas & Closures + Recursion Algorithms
""")