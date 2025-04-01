from dataclasses import dataclass
from itertools import count


@dataclass(slots=True)
class IdCounter:
    """Generates unique sequential IDs starting from 1."""

    _id = count(1)

    @classmethod
    def next(cls) -> int:
        return next(cls._id)


def seconds_to_milliseconds(seconds: float) -> float:
    return seconds * 1_000
