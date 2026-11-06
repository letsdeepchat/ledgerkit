"""Journal entries and postings.

Amounts are signed: a positive amount is a debit, a negative amount is a
credit. Every entry must balance, i.e. its postings sum to exactly zero.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Tuple

from .errors import InvalidEntryError, UnbalancedEntryError
from .money import ZERO, to_money


@dataclass(frozen=True)
class Posting:
    account: str
    amount: Decimal


@dataclass(frozen=True)
class JournalEntry:
    date: _dt.date
    memo: str
    postings: Tuple[Posting, ...]

    @classmethod
    def build(cls, date: _dt.date, memo: str, lines: Iterable) -> "JournalEntry":
        """Build and validate an entry from ``(account_code, amount)`` pairs."""
        postings = tuple(Posting(account, to_money(amount)) for account, amount in lines)
        entry = cls(date, memo, postings)
        entry.validate()
        return entry

    def validate(self) -> None:
        if isinstance(self.date, _dt.datetime) or not isinstance(self.date, _dt.date):
            raise InvalidEntryError("entry date must be a datetime.date")
        if len(self.postings) < 2:
            raise InvalidEntryError("an entry needs at least two postings")
        for posting in self.postings:
            if posting.amount == 0:
                raise InvalidEntryError("zero posting to %s" % posting.account)
        total = sum((p.amount for p in self.postings), ZERO)
        if total != 0:
            raise UnbalancedEntryError("entry is out of balance by %s" % total)

    @property
    def accounts(self) -> frozenset:
        return frozenset(p.account for p in self.postings)

    def amount_for(self, code: str) -> Decimal:
        """Net signed amount this entry posts to ``code``."""
        return sum((p.amount for p in self.postings if p.account == code), ZERO)
