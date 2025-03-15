

from abc import ABC, abstractmethod


class ValueParser[T, Z](ABC):

    @abstractmethod
    def parse(self, input: T) -> Z | None:
        ...


class StringParser[T](ValueParser[str, T]):
    pass
