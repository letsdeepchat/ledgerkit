# ledgerkit

A small, dependency-free double-entry bookkeeping library.

- `ChartOfAccounts` holds accounts (asset, liability, equity, income, expense).
- `Journal` stores balanced `JournalEntry` objects; amounts are signed
  `Decimal`s (debit positive, credit negative) with two decimal places.
- `ledgerkit.reports` computes balances, trial balances and account statements.
- `ledgerkit.importers.load_csv` imports entries from CSV.

Run the tests with `pytest -q`.
