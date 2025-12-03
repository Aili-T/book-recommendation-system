from typing import Generic, TypeVar, Callable, Any
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


# Maybe 类型：处理可能为空的值
class Maybe(Generic[T]):
    """Maybe 类型：表示可能存在或不存在的值"""

    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        raise NotImplementedError

    def bind(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        raise NotImplementedError

    def get_or_else(self, default: T) -> T:
        raise NotImplementedError

    def is_just(self) -> bool:
        raise NotImplementedError

    def is_nothing(self) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Just(Maybe[T]):
    """Just：包含一个值"""
    value: T

    def map(self, func: Callable[[T], U]) -> Maybe[U]:
        return Just(func(self.value))

    def bind(self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return func(self.value)

    def get_or_else(self, default: T) -> T:
        return self.value

    def is_just(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    def __str__(self):
        return f"Just({self.value})"


class Nothing(Maybe[T]):
    """Nothing：没有值"""

    def map(self, func: Callable[[T], U]) -> Maybe[U]:
        return Nothing()

    def bind(self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing()

    def get_or_else(self, default: T) -> T:
        return default

    def is_just(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def __str__(self):
        return "Nothing"


# Either 类型：处理可能成功或失败的操作
class Either(Generic[E, T]):
    """Either 类型：表示要么成功（Right）要么失败（Left）"""

    def map(self, func: Callable[[T], U]) -> 'Either[E, U]':
        raise NotImplementedError

    def bind(self, func: Callable[[T], 'Either[E, U]']) -> 'Either[E, U]':
        raise NotImplementedError

    def get_or_else(self, default: T) -> T:
        raise NotImplementedError

    def is_right(self) -> bool:
        raise NotImplementedError

    def is_left(self) -> bool:
        return not self.is_right()


@dataclass(frozen=True)
class Right(Either[E, T]):
    """Right：表示成功，包含结果值"""
    value: T

    def map(self, func: Callable[[T], U]) -> Either[E, U]:
        return Right(func(self.value))

    def bind(self, func: Callable[[T], Either[E, U]]) -> Either[E, U]:
        return func(self.value)

    def get_or_else(self, default: T) -> T:
        return self.value

    def is_right(self) -> bool:
        return True

    def __str__(self):
        return f"Right({self.value})"


@dataclass(frozen=True)
class Left(Either[E, T]):
    """Left：表示失败，包含错误信息"""
    error: E

    def map(self, func: Callable[[T], U]) -> Either[E, U]:
        return Left(self.error)

    def bind(self, func: Callable[[T], Either[E, U]]) -> Either[E, U]:
        return Left(self.error)

    def get_or_else(self, default: T) -> T:
        return default

    def is_right(self) -> bool:
        return False

    def __str__(self):
        return f"Left({self.error})"


# 工具函数
def maybe(value: T) -> Maybe[T]:
    """将值转换为Maybe"""
    if value is None:
        return Nothing()
    return Just(value)


def try_except(func: Callable[[], T], error_msg: str) -> Either[str, T]:
    """将可能抛出异常的代码转换为Either"""
    try:
        return Right(func())
    except Exception as e:
        return Left(f"{error_msg}: {str(e)}")