"""
Data-access functions for wallet balances and the transactions ledger.
Every wallet change is written to `transactions` in the same DB
transaction as the balance update, so the ledger and balance can
never drift apart.
"""

from models import user as user_model


def log_transaction(cursor, user_id, tx_type, amount, description):
    cursor.execute(
        """
        INSERT INTO transactions (user_id, type, amount, description)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, tx_type, amount, description),
    )


def credit(cursor, user_id, amount, description):
    user_model.credit_wallet(cursor, user_id, amount)
    log_transaction(cursor, user_id, "commission", amount, description)


def debit_for_withdrawal(cursor, user_id, amount, description):
    ok = user_model.debit_wallet(cursor, user_id, amount)
    if ok:
        log_transaction(cursor, user_id, "withdrawal", -amount, description)
    return ok


def get_transactions(cursor, user_id):
    cursor.execute(
        "SELECT * FROM transactions WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,),
    )
    return cursor.fetchall()
