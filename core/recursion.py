# core/recursion.py
from dataclasses import dataclass
from typing import List, Tuple, Optional


# 在这个文件中直接定义Tag类
@dataclass
class Tag:
    id: str
    name: str
    parent_id: Optional[str] = None
    children: List['Tag'] = None


# 只从domain导入Book，如果失败就在本地定义
try:
    from core.domain import Book
except ImportError:
    @dataclass(frozen=True)
    class Book:
        id: str
        title: str
        author: str
        genre: str
        year: int
        rating: float


def find_all_tags(tag: Tag) -> List[Tag]:
    """
    递归查找所有子标签
    """
    all_tags = [tag]

    if tag.children:
        for child in tag.children:
            child_tags = find_all_tags(child)
            all_tags.extend(child_tags)

    return all_tags


def find_tag_by_name(tag: Tag, name: str) -> Optional[Tag]:
    """
    根据名称递归查找标签
    """
    if tag.name.lower() == name.lower():
        return tag

    if tag.children:
        for child in tag.children:
            result = find_tag_by_name(child, name)
            if result is not None:
                return result

    return None


def print_tag_hierarchy(tag: Tag, level: int = 0) -> None:
    """
    递归打印标签层级结构
    """
    indent = "  " * level
    print(f"{indent}- {tag.name}")

    if tag.children:
        for child in tag.children:
            print_tag_hierarchy(child, level + 1)


def find_related_books(book: Book, all_books: Tuple[Book, ...]) -> Tuple[Book, ...]:
    """
    查找相关书籍（基于相同类型）
    """
    related = []
    for other_book in all_books:
        if other_book.id != book.id and other_book.genre == book.genre:
            related.append(other_book)
    return tuple(related)


def build_genre_hierarchy(books: Tuple[Book, ...]) -> Tag:
    """
    构建类型层次结构
    """
    # 创建根标签
    root = Tag("1", "All Genres")

    # 收集所有唯一的类型
    genres = set(book.genre for book in books)

    # 简化的层次结构构建
    fiction_tags = []
    nonfiction_tags = []

    for genre in genres:
        if genre in ["Sci-Fi", "Fantasy", "Classic"]:
            fiction_tags.append(Tag(f"sub_{genre}", genre))
        else:
            nonfiction_tags.append(Tag(f"sub_{genre}", genre))

    # 创建父类别
    fiction = Tag("cat_fiction", "Fiction", children=fiction_tags)
    nonfiction = Tag("cat_nonfiction", "Non-Fiction", children=nonfiction_tags)

    root.children = [fiction, nonfiction]
    return root


# 如果直接运行这个文件，提供示例
if __name__ == "__main__":
    print("🧪 Testing recursion functions...")

    # 创建测试标签结构
    root = Tag("1", "Programming")
    python = Tag("2", "Python")
    django = Tag("3", "Django")
    flask = Tag("4", "Flask")

    python.children = [django, flask]
    root.children = [python]

    print("1. Testing find_all_tags:")
    all_tags = find_all_tags(root)
    print(f"   Found {len(all_tags)} tags: {[tag.name for tag in all_tags]}")

    print("2. Testing find_tag_by_name:")
    found_tag = find_tag_by_name(root, "Django")
    print(f"   Found tag: {found_tag.name if found_tag else 'None'}")

    print("3. Testing tag hierarchy:")
    print_tag_hierarchy(root)

    print("✅ All recursion tests completed!")