"""
Data-access functions for the withdrawals table.
"""


def create_withdrawal(cursor, user_id, amount, method, account_details):
    cursor.execute(
        """
        INSERT INTO withdrawals (user_id, amount, method, account_details)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, amount, method, account_details),
    )
    return cursor.lastrowid


def get_history(cursor, user_id):
    cursor.execute(
        "SELECT * FROM withdrawals WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,),
    )
    return cursor.fetchall()


def get_all(cursor, status=None):
    if status:
        cursor.execute(
            """
            SELECT w.*, u.fullname, u.email
            FROM withdrawals w
            JOIN users u ON w.user_id = u.id
            WHERE w.status=%s
            ORDER BY w.created_at DESC
            """,
            (status,),
        )
    else:
        cursor.execute(
            """
            SELECT w.*, u.fullname, u.email
            FROM withdrawals w
            JOIN users u ON w.user_id = u.id
            ORDER BY w.created_at DESC
            """
        )
    return cursor.fetchall()


def get_by_id(cursor, withdrawal_id):
    cursor.execute("SELECT * FROM withdrawals WHERE id=%s", (withdrawal_id,))
    return cursor.fetchone()


def set_status(cursor, withdrawal_id, status, admin_note=None):
    cursor.execute(
        "UPDATE withdrawals SET status=%s, admin_note=%s WHERE id=%s",
        (status, admin_note, withdrawal_id),
    )
