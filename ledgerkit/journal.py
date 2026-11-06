"""The general journal: an in-memory store of posted entries."""

from __future__ import annotations

import datetime as _dt
from typing import Iterable, List, Optional, Tuple

from .accounts import ChartOfAccounts
from .entries import JournalEntry
from .errors import UnknownEntryError


class Journal:
    """Stores journal entries and hands out sequential entry ids (1, 2, 3...)."""

    def __init__(self, chart: Optional[ChartOfAccounts] = None) -> None:
        self.chart = chart if chart is not None else ChartOfAccounts()
        self._entries: dict[int, JournalEntry] = {}
        self._next_id = 1

    def post(self, entry: JournalEntry) -> int:
        """Validate ``entry`` and store it. Returns the new entry id."""
        entry.validate()
        for posting in entry.postings:
            self.chart.get(posting.account)
        entry_id = self._next_id
        self._next_id += 1
        self._entries[entry_id] = entry
        return entry_id

    def record(self, date: _dt.date, memo: str, lines: Iterable) -> int:
        """Convenience wrapper: build an entry from ``(code, amount)`` pairs and post it."""
        return self.post(JournalEntry.build(date, memo, lines))

    def get(self, entry_id: int) -> JournalEntry:
        try:
            return self._entries[entry_id]
        except KeyError:
            raise UnknownEntryError(entry_id) from None

    def entries(self) -> List[Tuple[int, JournalEntry]]:
        """All entries as ``(entry_id, entry)`` pairs ordered by (date, entry_id)."""
        return sorted(self._entries.items(), key=lambda item: (item[1].date, item[0]))

    def entries_for(self, code: str) -> List[Tuple[int, JournalEntry]]:
        """Entries that post to ``code``, in the same order as :meth:`entries`."""
        return [(eid, e) for eid, e in self.entries() if code in e.accounts]

    def __len__(self) -> int:
        return len(self._entries)
