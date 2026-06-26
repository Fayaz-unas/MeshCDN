from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Interval:
    """
    Represents a continuous range of owned chunks.

    Example:
        Interval(0, 99)
        Represents chunks:
        0, 1, 2, ..., 99
    """

    start: int
    end: int

    def __post_init__(self) -> None:
        """
        Validate interval boundaries.
        """
        if self.start < 0:
            raise ValueError("Interval start cannot be negative.")

        if self.end < 0:
            raise ValueError("Interval end cannot be negative.")

        if self.start > self.end:
            raise ValueError(
                "Interval start cannot be greater than end."
            )

    @property
    def length(self) -> int:
        """
        Number of chunks represented by this interval.

        Example:
            Interval(0, 9).length == 10
        """
        return self.end - self.start + 1

    def contains(self, chunk_index: int) -> bool:
        """
        Returns True if the chunk belongs to this interval.
        """
        return self.start <= chunk_index <= self.end

    def is_adjacent(self, other: "Interval") -> bool:
        """
        Returns True if two intervals touch each other.

        Example:
            [0-9] and [10-20]
        """
        return (
            self.end + 1 == other.start
            or other.end + 1 == self.start
        )

    def overlaps(self, other: "Interval") -> bool:
        """
        Returns True if intervals overlap.
        """
        return not (
            self.end < other.start
            or other.end < self.start
        )

    def can_merge(self, other: "Interval") -> bool:
        """
        Returns True if intervals overlap or are adjacent.
        """
        return (
            self.overlaps(other)
            or self.is_adjacent(other)
        )

    def merge(self, other: "Interval") -> "Interval":
        """
        Merge two compatible intervals.

        Raises:
            ValueError:
                If intervals are neither adjacent nor overlapping.
        """
        if not self.can_merge(other):
            raise ValueError(
                "Cannot merge non-adjacent intervals."
            )

        return Interval(
            start=min(self.start, other.start),
            end=max(self.end, other.end),
        )

    def to_list(self) -> list[int]:
        """
        Serialize interval.

        Example:
            Interval(0, 99)
            ->
            [0, 99]
        """
        return [self.start, self.end]

    @classmethod
    def from_list(cls, data: list[int]) -> "Interval":
        """
        Deserialize interval.

        Example:
            [0, 99]
            ->
            Interval(0, 99)
        """
        if len(data) != 2:
            raise ValueError(
                "Interval must contain exactly two integers."
            )

        return cls(
            start=data[0],
            end=data[1],
        )

    def __repr__(self) -> str:
        return f"Interval({self.start}, {self.end})"