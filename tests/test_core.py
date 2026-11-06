import datetime as dt
from decimal import Decimal

import pytest

from ledgerkit import (
    ChartOfAccounts, DuplicateAccountError, InvalidEntryError, Journal, JournalEntry,
    UnbalancedEntryError, UnknownAccountError, UnknownEntryError, account_statement,
    balance, load_csv, natural_balance, to_money, trial_balance,
)

D = dt.date


def make_journal():
    chart = ChartOfAccounts()
    chart.add("CASH", "Cash", "asset")
    chart.add("REV", "Revenue", "income")
    chart.add("RENT", "Rent", "expense")
    chart.add("EQ", "Owner equity", "equity")
    return Journal(chart)


def test_to_money_rounds_half_even_and_rejects_floats():
    assert to_money("1.005") == Decimal("1.00")
    assert to_money("1.015") == Decimal("1.02")
    assert to_money(3) == Decimal("3.00")
    with pytest.raises(TypeError):
        to_money(1.5)
    with pytest.raises(ValueError):
        to_money("abc")


def test_chart_rejects_duplicates_and_unknown_codes():
    chart = ChartOfAccounts()
    chart.add("A", "A", "asset")
    with pytest.raises(DuplicateAccountError):
        chart.add("A", "again", "asset")
    with pytest.raises(UnknownAccountError):
        chart.get("B")
    assert [a.code for a in chart] == ["A"]


def test_entry_validation():
    with pytest.raises(UnbalancedEntryError):
        JournalEntry.build(D(2026, 1, 1), "bad", [("CASH", "10"), ("REV", "-9")])
    with pytest.raises(InvalidEntryError):
        JournalEntry.build(D(2026, 1, 1), "one line", [("CASH", "0")])
    with pytest.raises(InvalidEntryError):
        JournalEntry.build(dt.datetime(2026, 1, 1), "datetime", [("CASH", "1"), ("REV", "-1")])


def test_post_assigns_sequential_ids_and_checks_accounts():
    j = make_journal()
    assert j.record(D(2026, 1, 2), "sale", [("CASH", "100"), ("REV", "-100")]) == 1
    assert j.record(D(2026, 1, 1), "capital", [("CASH", "50"), ("EQ", "-50")]) == 2
    with pytest.raises(UnknownAccountError):
        j.record(D(2026, 1, 1), "x", [("NOPE", "1"), ("CASH", "-1")])
    assert len(j) == 2
    assert [eid for eid, _ in j.entries()] == [2, 1]
    with pytest.raises(UnknownEntryError):
        j.get(99)


def test_balances_and_as_of():
    j = make_journal()
    j.record(D(2026, 1, 1), "capital", [("CASH", "1000"), ("EQ", "-1000")])
    j.record(D(2026, 1, 5), "rent", [("RENT", "300"), ("CASH", "-300")])
    j.record(D(2026, 1, 9), "sale", [("CASH", "250.50"), ("REV", "-250.50")])
    assert balance(j, "CASH") == Decimal("950.50")
    assert balance(j, "CASH", as_of=D(2026, 1, 5)) == Decimal("700.00")
    assert natural_balance(j, "REV") == Decimal("250.50")
    tb = trial_balance(j)
    assert sum(tb.values()) == 0
    assert list(tb) == ["CASH", "EQ", "RENT", "REV"]


def test_statement_running_balance_with_window():
    j = make_journal()
    j.record(D(2026, 1, 1), "capital", [("CASH", "1000"), ("EQ", "-1000")])
    j.record(D(2026, 1, 5), "rent", [("RENT", "300"), ("CASH", "-300")])
    j.record(D(2026, 1, 9), "sale", [("CASH", "250.50"), ("REV", "-250.50")])
    lines = account_statement(j, "CASH", start=D(2026, 1, 2), end=D(2026, 1, 8))
    assert [(l.entry_id, l.amount, l.running_balance) for l in lines] == [
        (2, Decimal("-300.00"), Decimal("700.00"))
    ]
    with pytest.raises(ValueError):
        account_statement(j, "CASH", start=D(2026, 2, 1), end=D(2026, 1, 1))


def test_csv_import_is_all_or_nothing():
    j = make_journal()
    good = "ref,date,memo,account,amount\nA,2026-01-01,cap,CASH,10\nA,2026-01-01,cap,EQ,-10\n"
    assert load_csv(j, good) == [1]
    bad = "ref,date,memo,account,amount\nB,2026-01-02,x,CASH,5\nB,2026-01-02,x,EQ,-5\nC,2026-01-02,y,CASH,1\nC,2026-01-02,y,EQ,-2\n"
    with pytest.raises(UnbalancedEntryError):
        load_csv(j, bad)
    assert len(j) == 1
