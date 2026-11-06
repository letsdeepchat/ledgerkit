"""Exception hierarchy for ledgerkit."""


class LedgerError(Exception):
    """Base class for every error raised by ledgerkit."""


class UnknownAccountError(LedgerError):
    """Raised when an account code is not in the chart of accounts."""


class DuplicateAccountError(LedgerError):
    """Raised when an account code is added to the chart twice."""


class InvalidEntryError(LedgerError):
    """Raised when a journal entry is structurally invalid."""


class UnbalancedEntryError(InvalidEntryError):
    """Raised when the postings of an entry do not sum to zero."""


class UnknownEntryError(LedgerError):
    """Raised when an entry id does not exist in the journal."""
