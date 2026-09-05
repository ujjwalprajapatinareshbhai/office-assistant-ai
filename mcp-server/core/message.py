from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    message_type: str
    current: int | None = None
    total: int | None = None
    filename: str | None = None
    data: Any = None
    error: str | None = None

    @staticmethod
    def progress(current: int, total: int, filename: str):
        return Message(
            message_type="progress",
            current=current,
            total=total,
            filename=filename
        )

    @staticmethod
    def result(data: Any):
        return Message(
            message_type="result",
            data=data
        )

    @staticmethod
    def error(error: str):
        return Message(
            message_type="error",
            error=error
        )