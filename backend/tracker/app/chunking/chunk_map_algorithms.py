from __future__ import annotations

from bisect import bisect_left
from typing import List

from app.chunking.interval import Interval


def find_insert_position(
    intervals: List[Interval],
    start: int,
) -> int:
    """
    Find the insertion position for a new interval.

    Time Complexity:
        O(log n)
    """

    starts = [interval.start for interval in intervals]

    return bisect_left(starts, start)


def merge_intervals(
    intervals: List[Interval],
) -> List[Interval]:
    """
    Merge overlapping or adjacent intervals.

    Example

    [0-5]
    [4-10]

    becomes

    [0-10]
    """

    if not intervals:
        return []

    intervals = sorted(
        intervals,
        key=lambda interval: interval.start,
    )

    merged = [intervals[0]]

    for current in intervals[1:]:

        previous = merged[-1]

        if previous.can_merge(current):
            merged[-1] = previous.merge(current)

        else:
            merged.append(current)

    return merged


def insert_interval(
    intervals: List[Interval],
    new_interval: Interval,
) -> List[Interval]:
    """
    Insert a new interval while keeping the list sorted.

    Automatically merges overlaps.
    """

    position = find_insert_position(
        intervals,
        new_interval.start,
    )

    updated = intervals.copy()

    updated.insert(
        position,
        new_interval,
    )

    return merge_intervals(updated)


def remove_chunk(
    intervals: List[Interval],
    chunk_index: int,
) -> List[Interval]:
    """
    Remove a single chunk.

    Splits intervals if necessary.
    """

    updated: List[Interval] = []

    for interval in intervals:

        if not interval.contains(chunk_index):
            updated.append(interval)
            continue

        # Entire interval removed

        if interval.length == 1:
            continue

        # Remove first chunk

        if chunk_index == interval.start:

            updated.append(
                Interval(
                    interval.start + 1,
                    interval.end,
                )
            )

            continue

        # Remove last chunk

        if chunk_index == interval.end:

            updated.append(
                Interval(
                    interval.start,
                    interval.end - 1,
                )
            )

            continue

        # Split interval

        updated.append(
            Interval(
                interval.start,
                chunk_index - 1,
            )
        )

        updated.append(
            Interval(
                chunk_index + 1,
                interval.end,
            )
        )

    return updated


def contains_chunk(
    intervals: List[Interval],
    chunk_index: int,
) -> bool:
    """
    Binary search lookup.

    Time Complexity

        O(log n)
    """

    left = 0
    right = len(intervals) - 1

    while left <= right:

        middle = (left + right) // 2

        interval = intervals[middle]

        if interval.contains(chunk_index):
            return True

        if chunk_index < interval.start:
            right = middle - 1

        else:
            left = middle + 1

    return False


def owned_chunk_count(
    intervals: List[Interval],
) -> int:
    """
    Total owned chunks.
    """

    return sum(
        interval.length
        for interval in intervals
    )


def missing_ranges(
    intervals: List[Interval],
    total_chunks: int,
) -> List[Interval]:
    """
    Compute missing chunk ranges.
    """

    missing: List[Interval] = []

    current = 0

    for interval in intervals:

        if current < interval.start:

            missing.append(
                Interval(
                    current,
                    interval.start - 1,
                )
            )

        current = interval.end + 1

    if current < total_chunks:

        missing.append(
            Interval(
                current,
                total_chunks - 1,
            )
        )

    return missing