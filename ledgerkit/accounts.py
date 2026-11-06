"""Chart of accounts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from .errors import DuplicateAccountError, UnknownAccountError


class AccountKind(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"

    @property
    def normal_sign(self) -> int:
        """+1 for debit-normal kinds, -1 for credit-normal kinds."""
        return 1 if self in (AccountKind.ASSET, AccountKind.EXPENSE) else -1


@dataclass(frozen=True)
class Account:
    code: str
    name: str
    kind: AccountKind


class ChartOfAccounts:
    """A registry of accounts keyed by their code."""

    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}

    def add(self, code: str, name: str, kind) -> Account:
        if not isinstance(code, str) or not code.strip():
            raise ValueError("account code must be a non-empty string")
        if code in self._accounts:
            raise DuplicateAccountError(code)
        account = Account(code, name, AccountKind(kind))
        self._accounts[code] = account
        return account

    def get(self, code: str) -> Account:
        try:
            return self._accounts[code]
        except KeyError:
            raise UnknownAccountError(code) from None

    def __contains__(self, code: object) -> bool:
        return code in self._accounts

    def __iter__(self) -> Iterator[Account]:
        return iter(sorted(self._accounts.values(), key=lambda a: a.code))

    def __len__(self) -> int:
        return len(self._accounts)
