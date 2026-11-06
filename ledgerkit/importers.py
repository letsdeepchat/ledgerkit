"""Import journal entries from CSV text.

Expected header: ``ref,date,memo,account,amount``. Rows sharing a ``ref`` form
one entry; refs are posted in order of first appearance. Dates are ISO-8601.
"""

from __future__ import annotations

import csv
import datetime as _dt
import io
from typing import Dict, List

from .entries import JournalEntry
from .errors import InvalidEntryError
from .journal import Journal

REQUIRED_COLUMNS = ("ref", "date", "memo", "account", "amount")


def load_csv(journal: Journal, text: str) -> List[int]:
    """Post every entry described by ``text``; returns the new entry ids in order.

    The import is all-or-nothing: every entry is built and validated before
    any of them is posted.
    """
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or any(c not in reader.fieldnames for c in REQUIRED_COLUMNS):
        raise InvalidEntryError("CSV must have columns: %s" % ", ".join(REQUIRED_COLUMNS))
    grouped: Dict[str, dict] = {}
    for row in reader:
        ref = row["ref"].strip()
        date = _dt.date.fromisoformat(row["date"].strip())
        group = grouped.setdefault(ref, {"date": date, "memo": row["memo"], "lines": []})
        if group["date"] != date:
            raise InvalidEntryError("ref %s has rows with different dates" % ref)
        group["lines"].append((row["account"].strip(), row["amount"].strip()))
    built = [JournalEntry.build(g["date"], g["memo"], g["lines"]) for g in grouped.values()]
    for entry in built:
        for posting in entry.postings:
            journal.chart.get(posting.account)
    return [journal.post(entry) for entry in built]
