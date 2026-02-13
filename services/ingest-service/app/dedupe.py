from collections import OrderedDict


class EventDeduplicator:
    """Bounded in-memory deduplicator keyed by event_id."""

    def __init__(self, max_ids: int = 50000) -> None:
        self.max_ids = max_ids
        self._seen: OrderedDict[str, None] = OrderedDict()

    def is_duplicate(self, event_id: str) -> bool:
        if event_id in self._seen:
            self._seen.move_to_end(event_id)
            return True

        self._seen[event_id] = None
        if len(self._seen) > self.max_ids:
            self._seen.popitem(last=False)
        return False

    def clear(self) -> None:
        self._seen.clear()
