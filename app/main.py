import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.domain import Book, User, Rating
from core.transforms import *

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


# Page configuration
st.set_page_config(page_title="Book Recommendation System", layout="wide")

# Sidebar menu
st.sidebar.title("Navigation Menu")
menu = st.sidebar.radio("Select Page", ["Overview", "Data", "Functional Core"])

# Load data
books_data, users_data, ratings_data = create_sample_data()

# Overview Page
if menu == "Overview":
    st.title("📊 System Overview")

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Books", len(books_data))
    with col2:
        st.metric("Total Users", len(users_data))
    with col3:
        st.metric("Total Ratings", len(ratings_data))
    with col4:
        avg_rating = get_average_rating(books_data)
        st.metric("Average Rating", f"{avg_rating:.2f}")

    st.subheader("Book Catalog")
    for book in books_data:
        st.write(f"- **{book.title}** by {book.author} ({book.year}) - ⭐ {book.rating}")

# Data Page
elif menu == "Data":
    st.title("📁 Data Management")

    st.success("✅ Sample data loaded successfully!")
    st.write(f"**Statistics:** {len(books_data)} books, {len(users_data)} users, {len(ratings_data)} ratings")

    # Display books in a table
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

    # Demo 1: Filter
    st.write("**1. Filter Function: Books published after 2000**")
    recent_books = filter_books_by_year(books_data, 2000)
    st.write("Results:", [b.title for b in recent_books])

    # Demo 2: Map
    st.write("**2. Map Function: Extract book titles and years**")
    book_info = list(map(lambda b: (b.title, b.year), books_data))
    st.write("Results:", book_info)

    # Demo 3: Reduce
    st.write("**3. Reduce Function: Calculate average book rating**")
    avg_rating = get_average_rating(books_data)
    st.write(f"Result: {avg_rating:.2f}")

    # Interactive demonstrations
    st.subheader("Interactive Filtering")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Filter by Genre**")
        selected_genre = st.selectbox("Select a genre:",
                                      ["Sci-Fi", "Fantasy", "Classic", "History", "Computer Science"])
        genre_books = filter_books_by_genre(books_data, selected_genre)
        st.write(f"**{selected_genre} Books ({len(genre_books)} found):**")
        for book in genre_books:
            st.write(f"- {book.title} ({book.year}) - ⭐ {book.rating}")

    with col2:
        st.write("**Filter by Year**")
        min_year = st.slider("Minimum publication year:", 1900, 2025, 2000)
        filtered_books = filter_books_by_year(books_data, min_year)
        st.write(f"**Books published after {min_year} ({len(filtered_books)} found):**")
        for book in filtered_books:
            st.write(f"- {book.title} - ⭐ {book.rating}")

# Footer information
st.sidebar.markdown("---")
st.sidebar.info("**Lab 1 Completed:** Pure Functions + Immutability + Higher-Order Functions")