from __future__ import annotations

from typing import List

from app.chunking.interval import Interval


def encode(
    intervals: List[Interval],
) -> List[List[int]]:
    """
    Convert intervals into a JSON-serializable format.

    Example

    [
        Interval(0, 100),
        Interval(200, 300)
    ]

    becomes

    [
        [0, 100],
        [200, 300]
    ]
    """

    return [
        interval.to_list()
        for interval in intervals
    ]


def decode(
    data: List[List[int]],
) -> List[Interval]:
    """
    Convert serialized intervals back into Interval objects.
    """

    return [
        Interval.from_list(item)
        for item in data
    ]