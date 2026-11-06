"""Read-only reports over a journal.

Every balance returned here is *signed* (debit positive, credit negative)
unless the function name says otherwise.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from .journal import Journal
from .money import ZERO


@dataclass(frozen=True)
class StatementLine:
    date: _dt.date
    entry_id: Optional[int]
    memo: str
    amount: Decimal
    running_balance: Decimal


def balance(journal: Journal, code: str, as_of: Optional[_dt.date] = None) -> Decimal:
    """Signed balance of ``code`` including every entry dated on or before ``as_of``.

    ``as_of=None`` includes every entry.
    """
    journal.chart.get(code)
    total = ZERO
    for _entry_id, entry in journal.entries_for(code):
        if as_of is not None and entry.date > as_of:
            continue
        total += entry.amount_for(code)
    return total


def natural_balance(journal: Journal, code: str, as_of: Optional[_dt.date] = None) -> Decimal:
    """Balance expressed in the account's normal direction (positive when 'normal')."""
    account = journal.chart.get(code)
    return balance(journal, code, as_of) * account.kind.normal_sign


def trial_balance(journal: Journal, as_of: Optional[_dt.date] = None) -> Dict[str, Decimal]:
    """Signed balance of every account in the chart, keyed by code."""
    return {account.code: balance(journal, account.code, as_of) for account in journal.chart}


def account_statement(
    journal: Journal,
    code: str,
    start: Optional[_dt.date] = None,
    end: Optional[_dt.date] = None,
) -> List[StatementLine]:
    """One line per entry touching ``code`` dated within [start, end] (inclusive).

    ``running_balance`` starts from the balance of everything dated before
    ``start``.
    """
    journal.chart.get(code)
    if start is not None and end is not None and start > end:
        raise ValueError("start must not be after end")
    running = ZERO
    lines: List[StatementLine] = []
    for entry_id, entry in journal.entries_for(code):
        amount = entry.amount_for(code)
        if start is not None and entry.date < start:
            running += amount
            continue
        if end is not None and entry.date > end:
            continue
        running += amount
        lines.append(StatementLine(entry.date, entry_id, entry.memo, amount, running))
    return lines
