"""
Homework 3: The Bounded Backpack -- starter.

Complete BoundedBackpack below. See HW3_The_Bounded_Backpack.md,
Part B, for the full requirements.
"""

import threading
import time
from typing import Any, List, Optional


class BackpackTimeoutError(Exception):
    """Raised when push()/pop() waits longer than its timeout without success."""


class BoundedBackpack:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._items: List[Any] = []
        self._condition = threading.Condition()

    def __len__(self) -> int:
        with self._condition:
            return len(self._items)

    def push(self, item: Any, timeout: Optional[float] = None) -> None:
        """
        Block while the backpack is full, waiting until space is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Insert at the top (LIFO), then wake any thread waiting in pop().
        """
        # TODO
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._condition:
            # while, not if: wait() can return spuriously, and another
            # producer may have taken the freed slot before we re-acquire.
            while len(self._items) >= self.capacity:
                remaining = self._remaining(deadline)
                if remaining is not None and remaining <= 0:
                    raise BackpackTimeoutError("push() timed out: backpack is full")
                self._condition.wait(remaining)
            self._items.append(item) 
            self._condition.notify_all()

    def pop(self, timeout: Optional[float] = None) -> Any:
        """
        Block while the backpack is empty, waiting until an item is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Remove and return the top item, then wake any thread waiting in push().
        """
        # TODO
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._condition:
            while not self._items:
                remaining = self._remaining(deadline)
                if remaining is not None and remaining <= 0:
                    raise BackpackTimeoutError("pop() timed out: backpack is empty")
                self._condition.wait(remaining)
            item = self._items.pop() 
            self._condition.notify_all()
            return item

    @staticmethod
    def _remaining(deadline: Optional[float]) -> Optional[float]:
        if deadline is None:
            return None
        return deadline - time.monotonic()