"""Money helpers.

All amounts in ledgerkit are ``decimal.Decimal`` values with exactly two
fractional digits. Floats are rejected outright because they cannot represent
most cent values exactly.
"""

from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def round_money(value: Decimal) -> Decimal:
    """Round a Decimal to cents using banker's rounding (ROUND_HALF_EVEN)."""
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)


def to_money(value) -> Decimal:
    """Convert ``value`` (str, int or Decimal) to a two-decimal amount."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("amounts must be str, int or Decimal, not %s" % type(value).__name__)
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("invalid amount: %r" % (value,)) from exc
    if not amount.is_finite():
        raise ValueError("invalid amount: %r" % (value,))
    return round_money(amount)
