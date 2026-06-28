from __future__ import annotations

from typing import Iterator

from app.chunking.interval import Interval
from app.chunking.chunk_map_algorithms import (
    contains_chunk,
    insert_interval,
    merge_intervals,
    missing_ranges,
    owned_chunk_count,
    remove_chunk,
)
from app.chunking.chunk_map_codec import (
    decode,
    encode,
)


class ChunkMap:
    """
    Represents chunk ownership using compressed intervals.

    Internally:

        [
            Interval(0, 99),
            Interval(200, 250)
        ]

    Serialized:

        [
            [0, 99],
            [200, 250]
        ]
    """

    def __init__(
        self,
        intervals: list[Interval] | None = None,
    ) -> None:

        self._intervals: list[Interval] = merge_intervals(
            intervals or []
        )

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def intervals(self) -> tuple[Interval, ...]:
        """
        Read-only view of intervals.
        """
        return tuple(self._intervals)

    # --------------------------------------------------
    # Modification
    # --------------------------------------------------

    def add(self, chunk_index: int) -> None:
        """
        Add a single chunk.
        """
        self.add_range(
            chunk_index,
            chunk_index,
        )

    def add_range(
        self,
        start: int,
        end: int,
    ) -> None:
        """
        Add a continuous chunk range.
        """

        self._intervals = insert_interval(
            self._intervals,
            Interval(start, end),
        )

    def remove(
        self,
        chunk_index: int,
    ) -> bool:
        """
        Remove a chunk.

        Returns
        -------
        bool

            True if removed.

            False if chunk didn't exist.
        """

        exists = contains_chunk(
            self._intervals,
            chunk_index,
        )

        if not exists:
            return False

        self._intervals = remove_chunk(
            self._intervals,
            chunk_index,
        )

        return True

    def clear(self) -> None:
        """
        Remove every interval.
        """

        self._intervals.clear()

    def merge(
        self,
        other: "ChunkMap",
    ) -> None:
        """
        Merge another ChunkMap into this ChunkMap.

        The resulting ChunkMap contains the union of all
        chunk ownership from both maps.
        """

        self._intervals = merge_intervals(
            [
                *self._intervals,
                *other._intervals,
            ]
        )

    def merged(
        self,
        other: "ChunkMap",
       ) -> "ChunkMap":
        """
        Return a new ChunkMap containing the union of
        this ChunkMap and another without modifying either.
        """

        merged = self.copy()
        merged.merge(other)
        return merged

    @classmethod
    def merge_all(
        cls,
        chunk_maps: list["ChunkMap"],
    ) -> "ChunkMap":
        """
        Merge multiple ChunkMaps into a single ChunkMap.
        """

        merged = cls()

        for chunk_map in chunk_maps:
            merged.merge(chunk_map)

        return merged
    

    
    def extend(
        self,
        intervals: list[Interval],
    ) -> None:
        """
        Merge a collection of intervals into this ChunkMap.
        """

        self._intervals = merge_intervals(
            [
                *self._intervals,
                *intervals,
            ]
        )

    # --------------------------------------------------
    # Queries
    # --------------------------------------------------

    def contains(
        self,
        chunk_index: int,
    ) -> bool:

        return contains_chunk(
            self._intervals,
            chunk_index,
        )

    def count(self) -> int:
        """
        Total owned chunks.
        """

        return owned_chunk_count(
            self._intervals,
        )

    def is_complete(
        self,
        total_chunks: int,
    ) -> bool:
        """
        Returns True if all chunks are owned.
        """

        return self.count() == total_chunks

    def missing_ranges(
        self,
        total_chunks: int,
    ) -> list[Interval]:

        return missing_ranges(
            self._intervals,
            total_chunks,
        )

    # --------------------------------------------------
    # Serialization
    # --------------------------------------------------

    def serialize(
        self,
    ) -> list[list[int]]:
        """
        JSON serializable representation.
        """

        return encode(
            self._intervals,
        )

    @classmethod
    def deserialize(
        cls,
        data: list[list[int]],
    ) -> "ChunkMap":
        """
        Create ChunkMap from serialized data.
        """

        return cls(
            decode(data),
        )

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def copy(self) -> "ChunkMap":
        """
        Deep copy.
        """

        return ChunkMap(
            list(self._intervals),
        )

    # --------------------------------------------------
    # Python Magic Methods
    # --------------------------------------------------

    def __contains__(
        self,
        chunk_index: int,
    ) -> bool:

        return self.contains(
            chunk_index,
        )

    def __len__(
        self,
    ) -> int:

        return self.count()

    def __iter__(
        self,
    ) -> Iterator[Interval]:

        return iter(
            self._intervals,
        )

    def __bool__(
        self,
    ) -> bool:

        return bool(
            self._intervals,
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"({self.serialize()})"
        )